"""
Finnhub Data Utilities Module.

https://finnhub.io/docs/api/

"""

import json
import os

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from tabulate import tabulate

import finnhub

def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):
    """
    Gets finnhub data saved and processed on disk.
    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        data_type (str): Type of data from finnhub to fetch. Can be insider_trans, SEC_filings, news_data, insider_senti, or fin_as_reported.
        data_dir (str): Directory where the data is saved.
        period (str): Default to none, if there is a period specified, should be annual or quarterly.
    """

    if period:
        data_path = os.path.join(
            data_dir,
            "finnhub_data",
            data_type,
            f"{ticker}_{period}_data_formatted.json",
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    data = open(data_path, "r")
    data = json.load(data)

    # filter keys (date, str in format YYYY-MM-DD) by the date range (str, str in format YYYY-MM-DD)
    filtered_data = {}
    for key, value in data.items():
        if start_date <= key <= end_date and len(value) > 0:
            filtered_data[key] = value
    return filtered_data


# Load environment variables from .env file
load_dotenv()

# Get API key from environment
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
BASE_URL = 'https://finnhub.io/api/v1/calendar/earnings'



def get_earnings_calendar(start_date, end_date):
    '''
    Get earnings calendar from Finnhub API.
    https://finnhub.io/api/v1/calendar/earnings?from=2025-07-01&to=2025-07-30&token=coaovg1r01qro9kpf6c0coaovg1r01qro9kpf6cg
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    '''
    # Define the date range
    params = {
        'from': start_date,
        'to': end_date,
        'token': FINNHUB_API_KEY
    }

    # Make the API request
    response = requests.get(BASE_URL, params=params)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data.get("earningsCalendar", []))
        df['eps_diff_percent'] = (df['epsActual'] - df['epsEstimate'])/df['epsActual']
        df['revenue_diff_percent'] = (df['revenueActual'] - df['revenueEstimate'])/df['revenueActual']
        return df
    else:
        print(f"Error {response.status_code}: {response.text}")

def get_company_profile(symbol):
    '''
    Get company profile from Finnhub API.
    https://finnhub.io/api/v1/stock/profile2?symbol=AAPL&token=coaovg1r01qro9kpf6c0coaovg1r01qro9kpf6cg

    '''
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    return finnhub_client.company_profile2(symbol=symbol)

def get_sec_filing(symbol):
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    return finnhub_client.filings(symbol=symbol, _from="2025-01-01", to="2025-0726")


if __name__ == "__main__":
    #response = get_company_profile('AAPL')
    df_earnings = get_earnings_calendar("2025-07-20", "2025-07-26")
    df_earnings = df_earnings.sort_values(by='revenueActual', ascending=False).head(50)
    company_profiles = {}
    for index, row in df_earnings.iterrows():
        company_profiles[row['symbol']] = get_company_profile(row['symbol'])
    # Dictionary with keys as rows (default)
    df_company_profiles = pd.DataFrame(company_profiles).T
    df_earning_with_profile = df_earnings.merge(df_company_profiles, left_on='symbol', right_on='ticker', how='inner')
    df_earning_with_profile.to_csv('eps_with_company.csv')
    #print(tabulate(df_earning_with_profile, headers='keys', tablefmt='psql'))
