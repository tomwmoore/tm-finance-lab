
import urllib
import pyodbc
import logging
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.dialects.mssql import DATETIME2, VARCHAR, FLOAT, BIGINT


def get_azure_engine(username: str, password: str, database: str = "tmfl_db", server: str = "tmfl-server.database.windows.net") -> create_engine:
    """
    Returns a SQLAlchemy engine for Azure SQL Database.
    
    Args:
        username (str): Azure SQL contained database user
        password (str): Password for the user
        database (str): Database name (default: tmfl_db)
        server (str): Azure SQL Server (default: tmfl-server.database.windows.net)
    
    Returns:
        SQLAlchemy engine 
    """

    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=900;"
    )

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    return engine



def get_analytics_azure_engine():
    return get_azure_engine(username="analytics_user", password="_for_@nalytics!123")  

def get_dashboard_azure_engine():
    return get_azure_engine(username="dashboard_user", password="_for_d@shbord!123!")  






def azure_upsert(df: pd.DataFrame, engine, table_name: str):
    """
    Upsert a pandas DataFrame into an Azure SQL table using a staging table + MERGE.
    Automatically escapes reserved keywords in SQL Server.
    Detects existing table column types if the table exists.
    Logs progress to console.
    """
    if df.empty:
        logging.info("DataFrame is empty. Nothing to upsert.")
        return

    # Parse schema and table
    if "." in table_name:
        schema, tbl = table_name.split(".")
    else:
        schema, tbl = "dbo", table_name

    staging_table = f"{tbl}_staging"

    with engine.connect() as conn:
        # Check if table exists and get column types
        col_query = text(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, DATETIME_PRECISION
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{tbl}';
        """)
        result = conn.execute(col_query).fetchall()

    dtype_mapping = {}
    if result:
        logging.info(f"Existing table detected: {table_name}. Using existing column types.")
        for row in result:
            col, dtype, char_max, dt_precision = row
            col_lower = col.lower()
            if "int" in dtype:
                dtype_mapping[col_lower] = BIGINT
            elif "float" in dtype or "decimal" in dtype:
                dtype_mapping[col_lower] = FLOAT
            elif "datetime" in dtype:
                dtype_mapping[col_lower] = DATETIME2(0)
            else:
                dtype_mapping[col_lower] = VARCHAR(char_max or 255)
    else:
        logging.info(f"Table {table_name} does not exist. Inferring types from DataFrame.")
        for col, dt in df.dtypes.items():
            if "datetime" in str(dt):
                dtype_mapping[col] = DATETIME2(0)
            elif "float" in str(dt):
                dtype_mapping[col] = FLOAT
            elif "int" in str(dt):
                dtype_mapping[col] = BIGINT
            else:
                dtype_mapping[col] = VARCHAR(255)

    # 1. Create staging table
    logging.info(f"Creating staging table {staging_table}.")
    df.head(0).to_sql(staging_table, engine, schema=schema, if_exists='replace', index=False, dtype=dtype_mapping)

    # 2. Insert data into staging
    logging.info(f"Inserting {len(df)} rows into staging table {staging_table}.")
    df.to_sql(staging_table, engine, schema=schema, if_exists='append', index=False, dtype=dtype_mapping)

    # 3. Detect primary key / unique constraints
    with engine.connect() as conn:
        key_query = text(f"""
            SELECT kcu.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
            WHERE tc.TABLE_SCHEMA = '{schema}' 
                AND tc.TABLE_NAME = '{tbl}'
                AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE')
            ORDER BY kcu.ORDINAL_POSITION;
        """)
        result = conn.execute(key_query).fetchall()
        conflict_cols = [row[0] for row in result]

    if not conflict_cols:
        raise ValueError(f"No primary key or unique index found on {table_name}. Upsert not possible.")

    # 4. Build MERGE statement (escape all column names)
    all_cols = list(df.columns)
    update_cols = [c for c in all_cols if c not in conflict_cols]

    merge_sql = f"""
    MERGE INTO [{schema}].[{tbl}] AS target
    USING [{schema}].[{staging_table}] AS source
    ON {" AND ".join([f"target.[{c}] = source.[{c}]" for c in conflict_cols])}
    WHEN MATCHED THEN
        UPDATE SET {", ".join([f"target.[{c}] = source.[{c}]" for c in update_cols])}
    WHEN NOT MATCHED THEN
        INSERT ({", ".join([f"[{c}]" for c in all_cols])})
        VALUES ({", ".join([f"source.[{c}]" for c in all_cols])});
    """

    # 5. Execute MERGE
    logging.info(f"Executing MERGE operation on {table_name}.")
    with engine.begin() as conn:
        conn.execute(text(merge_sql))

    # 6. Drop staging table
    logging.info(f"Dropping staging table {staging_table}.")
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE [{schema}].[{staging_table}]"))