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

def _generate_backward_quarters(from_year:int):
    '''Generate from current year & quarter to Q1 of the given year.
    '''
    quarters = ['2025Q2', '2025Q1']
    year= 2024
    while year >= from_year:
        quarters.append(f'{year}Q4')
        quarters.append(f'{year}Q3')
        quarters.append(f'{year}Q2')
        quarters.append(f'{year}Q1')
        year = year-1
    return quarters

def _earnings_to_markdown(earnings):
    '''convert earnings from alpha vantage to markdown.Extension

    Earnings will have the following data:
    - quarter
    - symbol
    - list of transcripts:
      - speaker
      - content
      - sentiment 
    '''
    md_output = f"### 📄 **{earnings['symbol']} {earnings['quarter']} Earnings Conference Call**\n\n"
    for entry in earnings['transcript']:
        speaker = entry.get("speaker", "Unknown")
        sentiment = entry.get("sentiment", None)
        content = entry.get("content", "")
        
        # Optional: include sentiment if available
        if sentiment is not None:
            md_output += f"👤 **{speaker}** _(Sentiment: {sentiment})_\n"
        else:
            md_output += f"👤 **{speaker}**\n"

        md_output += f"> {content.strip()}\n\n"
    
    return md_output

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
        qe = pd.DataFrame(self.get_earnings(symbol)['quarterlyEarnings']).set_index('reportedDate')

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

    def get_earnings_from(self, symbol: str, from_year:int):
        quarters = _generate_backward_quarters(from_year)
        transcripts = []
        markdown_transcript = ''
        for quarter in quarters:
            earnings = self.get_earnings_call(symbol, quarter)
            if len(earnings['transcript']) > 0:
                markdown_transcript+= _earnings_to_markdown(earnings)
                transcripts.append(json.dumps(earnings))
        return transcripts, markdown_transcript


