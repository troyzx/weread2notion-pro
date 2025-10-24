#!/usr/bin/env python3
"""
测试新的 query 实现
"""
import os
import json
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
database_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

print(f"NOTION_TOKEN: {notion_token[:20]}...")
print(f"DATABASE_ID: {database_id}\n")

try:
    client = Client(auth=notion_token)
    
    print("尝试新的 query 实现...")
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    body = {"filter": {"property": "标题", "title": {"equals": "设置"}}}
    
    response = client.client.post(
        url,
        content=json.dumps(body),
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"成功! 找到 {len(result.get('results', []))} 条记录")
    
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
