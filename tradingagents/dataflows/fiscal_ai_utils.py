"""
Fiscal AI Utilities Module

https://docs.fiscal.ai/docs/api-reference

As August 5th, it only support 24 companies.

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


class FiscalAiClient():
    def __init__(self, debug=False):
        # Get API key from environment
        self._fiscal_ai_api_key = os.getenv('FISCAL_AI_API_KEY')
        self._debug = debug

    def _query_rpc(self, url):
        '''Will append token to end of url and query.
        '''
        params = {
            "apiKey": self._fiscal_ai_api_key,
        }
        return pd.DataFrame(requests.get(f'{url}', params=params).json())
    
    def get_company_list(self):
        return self._query_rpc('https://api.fiscal.ai/v1/companies-list')