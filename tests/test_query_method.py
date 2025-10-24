#!/usr/bin/env python3
"""
测试 query 方法
"""
import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
setting_db_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

print(f"NOTION_TOKEN: {notion_token[:20]}...")
print(f"DATABASE_ID: {setting_db_id}\n")

try:
    client = Client(auth=notion_token)
    
    print("方式 1: 使用 client.request 方法（保留破折号）")
    print(f"ID: {setting_db_id}")
    
    result = client.request(
        path=f"databases/{setting_db_id}/query",
        method="POST",
        body={"filter": {"property": "标题", "title": {"equals": "设置"}}}
    )
    print(f"✓ 成功！找到 {len(result.get('results', []))} 条记录")
    
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}")
    print(f"消息: {e}")
    import traceback
    traceback.print_exc()
