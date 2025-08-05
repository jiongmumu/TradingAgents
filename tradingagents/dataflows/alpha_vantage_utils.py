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
from typing import Literal
from datetime import datetime, timedelta

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
    def __init__(self, debug=False):
        # Get API key from environment
        self._usage_table_name = 'AlphaVantage'
        self._api_usage_client = api_usage.ApiUsageClient(self._usage_table_name, 25)
        self._api_keys = [os.getenv('ALPHA_VANTAGE_API_KEY'),
                    os.getenv('ALPHA_VANTAGE_API_KEY2')]
        self._debug = debug

    def _query_rpc(self, url, result_is_csv = False):
        '''Will append token to end of url and query.
        '''
        return self._api_usage_client.query_rpc(url, self._api_keys, debug= self._debug, result_is_csv = result_is_csv)
    

    def get_earnings_call(self, symbol:str, quarter='2025Q2'):
        # get earnings transcript
        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALL_TRANSCRIPT&symbol={symbol}&quarter={quarter}'
        return self._query_rpc(url)
    
    def get_earnings_calendar(self, symbol:str|None = None, horizon_month: Literal[3,6,12] = 12):
        '''For this call, it will download a csv, and for some symbols, like NBIS, it doesn't have earnings calendar.
        '''
        symbol_filter = ''
        if symbol:
            symbol_filter = f'&symbol={symbol}'
        url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR{symbol_filter}&horizon={horizon_month}month'
        return self._query_rpc(url, result_is_csv=True)
    
    def get_news(self, symbols:list[str]|None=None,
                 topics: list[str]|None = None,
                 days_back=100, limit = 1000, prefilter = True):
        '''It is quite limited.. it doesn't offer many news I can find else where.
        If there are no news, even you specify tickers, it will return some random news, 
         the related symbols don't even have the ticker you specify. 
         But nice thing about it is it has summary to some sources I have no access,
           but many of those sources are nosiy, like 'Motley Fool, 'Benzinga' and 'Zacks Commentary' , just people's random comment. 
           Bloomberg api subscription almost 28K per year, so expensive, but that's mainly for institutional use, can't complain.
        '''

        formatted_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%dT0000")
        symbol_filter = ''
        if symbols:
            symbol_filter=f'&symbol={','.join(symbols)}'
        topic_filter = ''
        if topics:
            topic_filter = f'&topics={','.join(topics)}'
        news = self._query_rpc(f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT{symbol_filter}{topic_filter}&time_from={formatted_date}&limit={limit}')
        news_list = []
        fields= ['title', 'url', 'time_published', 'summary', 
                 'source', 'category_within_source', 'source_domain', 
                 'overall_sentiment_score', 'overall_sentiment_label']
        for feed in news['feed']:
            max_ticker = ''
            max_relevance_score = 0
            ticker_sentiment_score = 0
            for ts in feed['ticker_sentiment']:
                if float(ts['relevance_score']) > max_relevance_score:
                    max_relevance_score = float(ts['relevance_score'])
                    max_ticker = ts['ticker']
                    ticker_sentiment_score = float(ts['ticker_sentiment_score'])
            data = [max_ticker,ticker_sentiment_score,max_relevance_score]

            # override if there is only one symbol. 
            if symbols !=None and len(symbols) == 1:
                for ts in feed['ticker_sentiment']:
                    if ts['ticker'] == symbols[0]:
                        data = [symbols[0], float(ts['ticker_sentiment_score']), float(ts['relevance_score'])]
            for f in fields:
                data.append(feed[f])
            news_list.append(data)# symbols list empty or >1

        df_news = pd.DataFrame.from_records(news_list, columns=['ticker', 'ticker_sentiment_score', 'relevance_score']+fields)
        if prefilter:
            return df_news.query('relevance_score>0.5').query("source!='Motley Fool' and source != 'Benzinga' and source !='Zacks Commentary'" )
        else:
            return df_news
    
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


