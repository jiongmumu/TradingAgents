import sqlite3
from datetime import datetime, date
import requests
import pandas as pd
import json
from io import StringIO

conn = sqlite3.connect("api_usage.db")
cursor = conn.cursor()

class ApiUsageClient():
    def __init__(self, table_name, daily_limit):
        self._table_name = table_name
        self._daily_limit = daily_limit
    
    # def create_db(self):
    #     cursor.execute(f"""
    #     CREATE TABLE IF NOT EXISTS {self._table_name} (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         usage_date DATE DEFAULT (DATE('now')),
    #         api_key TEXT,
    #         content TEXT,
    #     )
    #     """)
    #     conn.commit()

    def get_cache(self, url:str):
        cursor.execute(f"""
            SELECT response FROM {self._table_name}
            WHERE url = ?
        """, (url,))
        rows= cursor.fetchall()
        if len(rows) >0:
            return json.loads(rows[0][0])
        return None

    def query_rpc(self, url, api_keys, result_is_csv = False, debug=False):
        '''Will append token to end of url and query.
        '''
        response_cache = self.get_cache(url)
        if response_cache is not None:
            return response_cache
        for api_key in api_keys:
            count = self.get_usage_count_today(api_key)
            if count < self._daily_limit:
                url_with_key= f'{url}&apikey={api_key}'
                if debug:
                    print(url_with_key)
                if result_is_csv:
                    with requests.Session() as s:
                        download = s.get(url_with_key)
                        decoded_content = download.content.decode('utf-8')
                        self.log_usage(api_key, url, decoded_content)
                        # Use pandas to read the CSV data from the decoded string
                        return pd.read_csv(StringIO(decoded_content))
                else:
                    response_json = requests.get(f'{url}&apikey={api_key}').json()
                    self.log_usage(api_key, url, json.dumps(response_json))
                    return response_json
        raise Exception("All API keys exceeded daily limit")
    
    def get_usage_count_today(self, api_key: str):
        today_str = date.today().isoformat()
        cursor.execute(f"""
            SELECT COUNT(*) FROM {self._table_name}
            WHERE api_key = ? AND usage_date = ?
        """, (api_key, today_str))
        return cursor.fetchone()[0]

    def log_usage(self, api_key: str, url: str, response: str):
        cursor.execute(f"INSERT INTO {self._table_name} (api_key, url, response) VALUES (?,?, ?)", (api_key,url,response))
        conn.commit()
