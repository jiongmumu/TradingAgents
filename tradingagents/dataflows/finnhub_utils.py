"""
Finnhub Data Utilities Module.

https://finnhub.io/docs/api/

"""

import json
import os
from datetime import datetime, timedelta
from typing import Literal

import finnhub
import pandas as pd
import pandas_market_calendars as mcal
import requests
import yfinance as yf
from dotenv import load_dotenv
from tabulate import tabulate


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
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/calendar/earnings"


def get_earnings_calendar(start_date: str, end_date: str):
    """
    Get earnings calendar from Finnhub API.
    https://finnhub.io/api/v1/calendar/earnings?from=2025-07-01&to=2025-07-30&token=coaovg1r01qro9kpf6c0coaovg1r01qro9kpf6cg

    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    """
    # Define the date range
    params = {"from": start_date, "to": end_date, "token": FINNHUB_API_KEY}

    # Make the API request
    response = requests.get(BASE_URL, params=params)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data.get("earningsCalendar", []))
        df["eps_diff_percent"] = (df["epsActual"] - df["epsEstimate"]) / df["epsActual"]
        df["revenue_diff_percent"] = (df["revenueActual"] - df["revenueEstimate"]) / df[
            "revenueActual"
        ]
        return df
    else:
        print(f"Error {response.status_code}: {response.text}")


def previous_open_market_day(date_str: str) -> str:
    nyse = mcal.get_calendar("NYSE")
    date = datetime.strptime(date_str, "%Y-%m-%d")

    # Get the previous 10 business days including the target day
    schedule = nyse.schedule(
        start_date=(date - timedelta(days=15)).strftime("%Y-%m-%d"),
        end_date=date.strftime("%Y-%m-%d"),
    )

    # Find all market open days before the given date
    open_days = schedule.index[schedule.index < date].sort_values()

    if not open_days.empty:
        return open_days[-1].strftime("%Y-%m-%d")
    else:
        raise ValueError("No previous open market day found")


def next_open_market_day(date_str: str) -> str:
    nyse = mcal.get_calendar("NYSE")
    date = datetime.strptime(date_str, "%Y-%m-%d")

    # Get the previous 10 business days including the target day
    schedule = nyse.schedule(
        start_date=date, end_date=(date + timedelta(days=15)).strftime("%Y-%m-%d")
    )

    # Find all market open days before the given date
    open_days = schedule.index[schedule.index > date].sort_values()

    if not open_days.empty:
        return open_days[0].strftime("%Y-%m-%d")
    else:
        raise ValueError("No next open market day found")


def get_earnings_and_profiles(
    earning_release_date: str, hour: Literal["amc", "bmo"], stock_limit=50
):
    df_earnings = get_earnings_calendar(earning_release_date, earning_release_date)
    df_earnings = df_earnings.sort_values(by="revenueActual", ascending=False).head(
        stock_limit
    )
    company_profiles = {}

    for _, row in df_earnings.iterrows():
        try:
            company_profiles[row["symbol"]] = get_company_profile(row["symbol"])
        except Exception as e:
            print(e)

    # Dictionary with keys as rows (default)
    df_company_profiles = pd.DataFrame(company_profiles).T
    if hour == "amc":
        # next day
        before_earning_date = earning_release_date
        after_earning_date = next_open_market_day(earning_release_date)
    elif hour == "bmo":
        # the same day
        before_earning_date = previous_open_market_day(earning_release_date)
        after_earning_date = earning_release_date
    stock_data = (
        yf.download(df_earnings.symbol.tolist(), period="1y")
        .stack(level=1)
        .reset_index()
    )
    df_ep_p = (
        stock_data.query(f'Date == "{before_earning_date}"')
        .merge(
            stock_data.query(f'Date == "{after_earning_date}"'),
            on="Ticker",
            suffixes=["", "_1"],
        )
        .merge(df_earnings, left_on="Ticker", right_on="symbol")
    )
    df_ep_p["change_after_earning"] = (df_ep_p["Open_1"] - df_ep_p["Close"]) / df_ep_p[
        "Close"
    ]
    df_ep_p["change_after_earning_cc"] = (
        df_ep_p["Close_1"] - df_ep_p["Close"]
    ) / df_ep_p["Close"]
    df_prices_profile = df_ep_p[
        [
            "date",
            "symbol",
            "change_after_earning",
            "change_after_earning_cc",
            "epsActual",
            "epsEstimate",
            "eps_diff_percent",
            "revenueActual",
            "revenueEstimate",
            "revenue_diff_percent",
        ]
    ].merge(df_company_profiles, left_on="symbol", right_on="ticker", how="inner")
    return df_prices_profile.query(f'date == "{earning_release_date}"').sort_values(
        "marketCapitalization", ascending=False
    )


def get_company_profile(symbol, use_finnhub_for_profile=False):
    """
    Get company profile from Finnhub API.
    https://finnhub.io/api/v1/stock/profile2?symbol=AAPL&token=coaovg1r01qro9kpf6c0coaovg1r01qro9kpf6cg

    No eps, has marketCapitalization, no other statistics.

    """
    if use_finnhub_for_profile:
        finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
        return finnhub_client.company_profile2(symbol=symbol)
    else:
        info = yf.Ticker(symbol).info
        data = {
            k: pd.to_numeric(info[k], errors="coerce")
            for k in [
                "beta",
                "revenuePerShare",
                "revenueGrowth",
                "priceToSalesTrailing12Months",
                "priceToBook",
                "priceEpsCurrentYear",
                "fiftyDayAverage",
                "profitMargins",
                "trailingEps",
                "forwardEps",
                "totalRevenue",
            ]
            if k in info
        }
        data["ticker"] = symbol
        # so it has the same key as from finnhub, so it can be sorted based on this key.
        data["marketCapitalization"] = float(info["marketCap"])
        data["shortName"] = info["shortName"]
        data["industry"] = info["industry"]
        return data


def get_sec_filing(symbol):
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    return finnhub_client.filings(symbol=symbol, _from="2025-01-01", to="2025-0726")


if __name__ == "__main__":
    # response = get_company_profile('AAPL')
    df_earnings = get_earnings_calendar("2025-07-20", "2025-07-26")
    df_earnings = df_earnings.sort_values(by="revenueActual", ascending=False).head(50)
    company_profiles = {}
    for index, row in df_earnings.iterrows():
        company_profiles[row["symbol"]] = get_company_profile(row["symbol"])
    # Dictionary with keys as rows (default)
    df_company_profiles = pd.DataFrame(company_profiles).T
    df_earning_with_profile = df_earnings.merge(
        df_company_profiles, left_on="symbol", right_on="ticker", how="inner"
    )
    df_earning_with_profile.to_csv("eps_with_company.csv")
    # print(tabulate(df_earning_with_profile, headers='keys', tablefmt='psql'))
