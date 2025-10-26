import pandas as pd
import numpy as np
import yfinance as yf




def get_industry(symbol):
    stock = yf.Ticker(symbol)
    info = stock.get_info()
    return info.get('industry',None) # get industry if in dict keys, return None if it doesn't exist


def get_sector(symbol):
    stock = yf.Ticker(symbol)
    info = stock.get_info()
    return info.get('sector',None) # get sector if in dict keys, return None if it doesn't exist