import pandas as pd
import numpy as np

import src.utils.indicators as ind

class FeaturePipeline:
    def __init__(self,df,config = None):
        self.df = df.copy()

        # each config can have multiple entries
        default_config = {
            'rsi_periods': [14],          # Can compute multiple RSIs
            'sma_periods': [20, 50],      # Multiple SMAs
            'bollinger_periods': [14]
        }        

        # Merge user config with defaults
        self.config = default_config if config is None else {**default_config, **config}


    def get_indicators(self):
        
        # RSI
        for period in self.config['rsi_periods']:
            col_name = f'rsi_{period}'
            self.df[col_name] = ind.compute_rsi(self.df['close'], period=period)

        # Bollinger Bands
        for period in self.config['bollinger_periods']:
            col_upper = f'bb_upper_{period}'
            col_lower = f'bb_lower_{period}'

            upper_band, lower_band = ind.compute_bollinger_bands(self.df['close'],period = period)
            self.df[col_upper] = upper_band
            self.df[col_lower] = lower_band            



    def run_pipeline(self):
        self.get_indicators()

        return self.df