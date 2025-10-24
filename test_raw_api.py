#!/usr/bin/env python3
"""
使用原始 httpx 测试 API 调用
"""
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
database_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

headers = {
    "Authorization": f"Bearer {notion_token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

url = f"https://api.notion.com/v1/databases/{database_id}/query"
body = {"filter": {"property": "标题", "title": {"equals": "设置"}}}

print(f"URL: {url}")
print(f"Body: {body}\n")

try:
    with httpx.Client() as client:
        response = client.post(url, json=body, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
