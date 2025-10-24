#!/usr/bin/env python3
"""
测试通过 notion_client 的 request 方法
"""
import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
database_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

print(f"NOTION_TOKEN: {notion_token[:20]}...")
print(f"DATABASE_ID: {database_id}\n")

try:
    client = Client(auth=notion_token)
    
    print("调用 client.request()...")
    result = client.request(
        path=f"databases/{database_id}/query",
        method="POST",
        body={"filter": {"property": "标题", "title": {"equals": "设置"}}}
    )
    
    print(f"✓ 成功！")
    print(f"结果: {result}")
    
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}")
    print(f"消息: {e}")
    
    # 尝试获取更多信息
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text[:200]}")
