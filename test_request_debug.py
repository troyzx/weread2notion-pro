#!/usr/bin/env python3
"""
测试正确的 request 方法调用格式
"""
import os
from dotenv import load_dotenv
from notion_client import Client
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
database_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

print(f"NOTION_TOKEN: {notion_token[:20]}...")
print(f"DATABASE_ID: {database_id}\n")

try:
    client = Client(auth=notion_token, log_level=logging.DEBUG)
    
    print("尝试方式 1: 直接使用 client.request()")
    result = client.request(
        path=f"databases/{database_id}/query",
        method="POST",
        body={"filter": {"property": "标题", "title": {"equals": "设置"}}}
    )
    print(f"成功: {result}")
    
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
