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
        self._daily_limit = 25
        self._api_usage_client = api_usage.ApiUsageClient(self._usage_table_name)
        self._api_keys = [os.getenv('ALPHA_VANTAGE_API_KEY'),
                    os.getenv('ALPHA_VANTAGE_API_KEY2')]

    def query_rpc(self, url):
        '''Will append token to end of url and query.
        '''
        for api_key in self._api_keys:
            count = self._api_usage_client.get_usage_count_today(api_key)
            if count < self._daily_limit:
                updated_url = f'{url}&apikey={api_key}'
                response_json = requests.get(updated_url).json()
                self._api_usage_client.log_usage(api_key, url, json.dumps(response_json))
                return pd.DataFrame(response_json)
        raise Exception("All API keys exceeded daily limit")

    def get_earnings_call(self, symbol:str, quarter='2025Q2'):
        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol={symbol}&quarter={quarter}'
        return self.query_rpc(url)
