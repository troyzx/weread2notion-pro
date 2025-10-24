#!/usr/bin/env python3
"""
测试禁用 SSL 验证
"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
database_id = "2968ad53-45be-81df-aa8e-dc55283982f6"

print(f"NOTION_TOKEN: {notion_token[:20]}...")
print(f"DATABASE_ID: {database_id}\n")

try:
    # 创建不验证 SSL 的客户端
    http_client = httpx.Client(verify=False)
    client = Client(auth=notion_token, client=http_client)
    
    print("尝试禁用 SSL 验证...")
    result = client.request(
        path=f"databases/{database_id}/query",
        method="POST",
        body={"filter": {"property": "标题", "title": {"equals": "设置"}}}
    )
    print(f"成功！")
    print(f"找到 {len(result.get('results', []))} 条记录")
    
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    http_client.close()
