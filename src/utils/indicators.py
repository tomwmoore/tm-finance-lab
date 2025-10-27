import pandas as pd
import numpy as np


def compute_rolling_avg(data : pd.Series, period : int):

    """
    Computes Simple Moving Average (SMA)
    """

    return data.rolling(window=period).mean()


def compute_bollinger_bands(data : pd.Series, period : int):

    """
    Computes Upper & Lower Bollinger Band given price data 
    """

    moving_avg = compute_rolling_avg(data,period=period)
    moving_std = 2*data.rolling(window=period).std()

    upper_band = moving_avg + moving_std
    lower_band = moving_avg - moving_std
    
    return upper_band, lower_band


def compute_rsi(data : pd.Series, period : int):

    """
    Function computes Relative Strength Index (RSI) for a given price series and period

    Parameters
    ----------------
    data: pd.Series
        pandas series (ie df['close']) of price data

    period: int
        back looking period over which RSI is calculated 
    
    Returns
    ----------------
    rsi: int
        
    """

    delta = data.diff() # calcs x[i] - x[i-1]
    gain = delta.clip(lower = 0) # any delta below 0 is made 0 to get gains day
    loss = -delta.clip(upper = 0) # any delta above 0 is made 0 to get losses day, covnerted to absolute value

    # get average of gains and losses
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain/avg_loss
    rsi = 100 - (100/(1+rs))

    return rsi


