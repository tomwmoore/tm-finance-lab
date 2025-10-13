import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # GROSS AND HACKY SO YOU CAN USE src 

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

from src.utils.db_azure import get_analytics_azure_engine
from src.utils.db_azure import azure_upsert


def update_prices(industry: str, start_date: str, end_date:str):

    
    print(f"Debug: Getting price data for industry {industry} and dates: {start_date} to {end_date}...")
    
    # Get list of tickers from given industry from asset header
    query_symbol = f"""
                    select symbol 
                    from asset_header
                    where industry = '{industry}'
                    """

    engine = get_analytics_azure_engine()

    symbols = pd.read_sql(query_symbol,engine)

    # pull price data
    data = yf.download(symbols['symbol'].tolist(), interval= '1d', group_by='ticker', start = start_date, end = end_date)

    # Clean up multi-index column names to just be the feature names (close, open etc) & make lowercase
    data = data.stack(level=0,future_stack=True).rename_axis(['Date', 'Ticker']).reset_index(level=1)

    # remote date as the index
    data = data.reset_index()

    data.columns = [col.lower() for col in data.columns]

    # add current timestamp for troubleshooting
    data['updated_at'] = pd.Timestamp.now()

    data = data.rename(columns = {"ticker":"symbol"})

    # Upsert to db
    print(f"Debug: Upserting price data to stock_prices...")

    azure_upsert(data,engine,'stock_prices')

    print(f"Success: Updating price data complete")





# for testing or running individually
if __name__ == '__main__':
    print('Running update_prices.py')
    update_prices(industry='Oil & Gas E&P', start_date='2025-10-01', end_date='2025-10-13')
