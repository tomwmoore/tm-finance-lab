import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # GROSS AND HACKY SO YOU CAN USE src 

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime


from src.utils.db_azure import get_analytics_azure_engine
from src.utils.db_azure import azure_upsert


def update_prices(industry: str, start_date: str, end_date:str):

    # Get list of tickers from given industry from asset header
    query_symbol = f"""
                    select symbol 
                    from asset_header
                    where industry = '{industry}'
                    """

    engine = get_analytics_azure_engine()

    symbols = pd.read_sql(query_symbol,engine)




# for testing
if __name__ == '__main__':
    print('Testing update_prices.py')
    update_prices(industry='Oil & Gas E&P', start_date='2025-07-07 13:35:00.000', end_date='2025-07-20 13:35:00.000')