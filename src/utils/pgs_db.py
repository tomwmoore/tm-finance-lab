from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import text, inspect

def get_pgs_engine():
    """
    Returns a sqlalchemy engine for PostgreSQL 
    """
    user = 'trader'
    password = 'trader'
    host = 'localhost'
    port = 5432
    dbname = 'finance'

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    return engine




def pgs_upsert(df: pd.DataFrame, engine, table_name: str):
    """
    Upsert a pandas DataFrame into a PostgreSQL table.
    -- Replaces data when index already exists, appends if indexes don't yet exist
    -- Returns error if pgs table doesn't have indices set yet

    """
    if df.empty:
        return

    # Extract schema + table parts
    if "." in table_name:
        schema, tbl = table_name.split(".")
    else:
        schema, tbl = "public", table_name

    # 1. Detect conflict columns from primary key or unique indexes
    conflict_query = text(f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = '{tbl}'   
            AND tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
        ORDER BY kcu.ordinal_position;
    """)
    with engine.connect() as conn:
        result = conn.execute(conflict_query)
        conflict_cols = [row[0] for row in result.fetchall()]

    if not conflict_cols:
        raise ValueError(f"No unique index or primary key found on {table_name}. Upsert not possible.")

    # 2. Decide which columns to update
    update_cols = [c for c in df.columns if c not in conflict_cols]

    # 3. Build SQL
    cols = list(df.columns)
    col_names = ", ".join(cols)
    placeholders = ", ".join([f":{c}" for c in cols])

    conflict_target = ", ".join(conflict_cols)
    update_stmt = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

    query = text(f"""
        INSERT INTO {schema}.{tbl} ({col_names})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_target})
        DO UPDATE SET {update_stmt};
    """)

    # 4. Execute in bulk
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(query, records)
