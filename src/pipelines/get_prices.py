import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # GROSS AND HACKY SO YOU CAN USE src 

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

from src.utils.db_azure import get_analytics_azure_engine
from src.utils.db_azure import azure_upsert


def get_yf_prices(symbols : list, start_date: str, end_date : str, interval : str = '1d'):

    '''
    Returns a pandas dataframe with price data from yfinance for given period and list of symbols. 
    Data is extracted and column names are standardized. 
    '''

    # pull price data
    data = yf.download(symbols, interval= interval, group_by='ticker', start = start_date, end = end_date)

    # Clean up multi-index column names to just be the feature names (close, open etc) & make lowercase
    data = data.stack(level=0,future_stack=True).rename_axis(['Date', 'Ticker']).reset_index(level=1)

    # remote date as the index
    data = data.reset_index()

    data.columns = [col.lower() for col in data.columns]

    # add current timestamp for troubleshooting
    data['updated_at'] = pd.Timestamp.now()

    data = data.rename(columns = {"ticker":"symbol"})

    return data


def update_stock_prices(industry: str, start_date: str, end_date:str):

    print(f"Debug: Getting price data for industry {industry} and dates: {start_date} to {end_date}...")
    
    # Get list of tickers from given industry from asset header
    query_symbol = f"""
                    select symbol 
                    from asset_header
                    where industry = '{industry}'
                    and asset_type = 'stock'
                    """

    engine = get_analytics_azure_engine()

    symbols = pd.read_sql(query_symbol,engine)
    symbols = symbols['symbol'].tolist()

    # get price data
    data = get_yf_prices(symbols=symbols, 
                         start_date=start_date,
                         end_date=end_date,
                         interval='1d')

    # Upsert to db
    print(f"Debug: Upserting price data to stock_prices...")
    azure_upsert(data,engine,'stock_prices')
    print(f"Success: Updating price data complete")



def update_oil_prices(start_date : str, end_date : str):

    print(f"Debug: Getting oil price data for dates: {start_date} to {end_date}...")

    data = get_yf_prices(symbols=['CL=F'],start_date=start_date, end_date=end_date, interval = '1d', )

    # Upsert to db
    print(f"Debug: Upserting price data to stock_prices...")
    engine = get_analytics_azure_engine()
    azure_upsert(data,engine,'stock_prices')
    print(f"Success: Updating price data complete")



# for testing or running individually
if __name__ == '__main__':
    print('Running get_prices.py')
    start_date = '2020-10-28'
    end_date ='2025-10-28'


    update_stock_prices(industry='Oil & Gas E&P', start_date=start_date, end_date=end_date)
    update_stock_prices(industry='Oil & Gas Integrated', start_date=start_date, end_date=end_date)
    update_oil_prices(start_date=start_date, end_date=end_date)
