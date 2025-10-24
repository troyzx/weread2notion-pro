#!/usr/bin/env python3
"""
诊断脚本 - 检查 Notion API 连接
"""
import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
notion_page = os.getenv("NOTION_PAGE")

print(f"NOTION_TOKEN: {notion_token[:20]}..." if notion_token else "NOTION_TOKEN: NOT SET")
print(f"NOTION_PAGE: {notion_page}")

if not notion_token:
    print("错误: NOTION_TOKEN 未设置")
    exit(1)

try:
    print("\n尝试创建 Notion 客户端...")
    client = Client(auth=notion_token)
    print("✓ 客户端创建成功")
    
    print("\n尝试获取用户信息...")
    user = client.users.me()
    print(f"✓ 用户获取成功: {user.get('name')}")
    
    print("\n尝试检索页面...")
    import re
    match = re.search(r"[a-f0-9]{32}", notion_page)
    if match:
        page_id = match.group(0)
    else:
        page_id = notion_page
    
    page = client.pages.retrieve(page_id)
    print(f"✓ 页面检索成功")
    
except Exception as e:
    print(f"✗ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
