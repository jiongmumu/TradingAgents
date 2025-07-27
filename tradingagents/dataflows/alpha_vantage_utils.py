"""
Alpha vantage Data Utilities Module

https://www.alphavantage.co/documentation/

"""

import requests
import pandas as pd
from dotenv import load_dotenv
import os
import api_usage
import json

# Load environment variables from .env file
load_dotenv()

class AlphaVantageClient():
    def __init__(self):
        # Get API key from environment
        self._usage_table_name = 'AlphaVantage'
        self._api_usage_client = api_usage.ApiUsageClient(self._usage_table_name, 25)
        self._api_keys = [os.getenv('ALPHA_VANTAGE_API_KEY'),
                    os.getenv('ALPHA_VANTAGE_API_KEY2')]

    def _query_rpc(self, url):
        '''Will append token to end of url and query.
        '''
        return self._api_usage_client.query_rpc(url, self._api_keys)

    def get_earnings_call(self, symbol:str, quarter='2025Q2'):
        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol={symbol}&quarter={quarter}'
        return self._query_rpc(url)
    
    def get_earnings(self, symbol:str):
        url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}'
        return self._query_rpc(url)
    
    def add_eps_column(self, df: pd.DataFrame, symbol:str):
        '''Add eps column to existing pandas.DataFrame.

        The computation maybe different from other websites. But it is just an estimate of EPS.
        We use report date as cut off, then look back adding 4 existing EPS. 
        Not using quarter ending date here, because until report date, we don't know EPS.

        df should have index which is date.
        '''
        qe = pd.DataFrame(self.get_earnings('META')['quarterlyEarnings']).set_index('reportedDate')

        # shift so latest reported date has value
        eps_rolling = qe['reportedEPS'].rolling(window=4).sum().shift(-3)
        previous_date = None
        for date, eps in eps_rolling.dropna().items():
            if previous_date is None:
                df.loc[df.index > date, 'eps'] = eps
            else:
                df.loc[(df.index > date) & (df.index <= previous_date), 'eps'] = eps
            previous_date =date
        return df



