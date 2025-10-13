import pandas as pd
import numpy as np

def compute_rsi(data, period):

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


