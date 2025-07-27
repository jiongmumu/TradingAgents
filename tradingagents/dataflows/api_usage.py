import sqlite3
from datetime import datetime, date
import requests


conn = sqlite3.connect("api_usage.db")
cursor = conn.cursor()

class ApiUsageClient():
    def __init__(self, table_name):
        self._table_name = table_name
    
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
