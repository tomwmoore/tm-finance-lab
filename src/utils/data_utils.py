import pandas as pd

def normalize_to_first_value(df : pd.DataFrame,columns : list):
    """
    Normalizes values to first NaN value in given columns
    
    Returns a df with given columns in normalized format
    """
    for col in columns:
        if col in df:
            first_valid = df[col].dropna().iloc[0]
            df[col] = df[col] / first_valid

    return df