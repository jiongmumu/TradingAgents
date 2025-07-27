import sqlite3
from datetime import datetime, date
import requests
import pandas as pd
import json

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

    def query_rpc(self, url, api_keys):
        '''Will append token to end of url and query.
        '''
        response_cache = self.get_cache(url)
        if response_cache is not None:
            return response_cache
        for api_key in api_keys:
            count = self.get_usage_count_today(api_key)
            if count < self._daily_limit:
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

    # def get_available_api_key(data):
    #     for api_key in API_KEYS:
    #         count = get_usage_count_today(api_key)
    #         if count < DAILY_LIMIT:
    #             log_usage(api_key)
    #             response = requests.post("https://your.rpc.endpoint", headers={"Authorization": api_key}, json=data)
    #             return response.json()
    #     raise Exception("All API keys exceeded daily limit")
