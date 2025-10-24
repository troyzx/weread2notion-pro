#!/usr/bin/env python3
"""
测试 WeRead Cookie 和 API
"""
import os
from dotenv import load_dotenv
import requests
from requests.utils import cookiejar_from_dict
import re

load_dotenv()

cookie_str = os.getenv("WEREAD_COOKIE")

print("=== Cookie 字符串 ===")
print(cookie_str[:100] + "..." if len(cookie_str) > 100 else cookie_str)
print(f"长度: {len(cookie_str)}\n")

# 解析 cookie
print("=== 解析 Cookie ===")
cookies_dict = {}
pattern = re.compile(r'([^=]+)=([^;]+);?\s*')
matches = pattern.findall(cookie_str)

print(f"找到 {len(matches)} 个 cookie:")
for key, value in matches:
    print(f"  {key}: {value[:30]}..." if len(value) > 30 else f"  {key}: {value}")

cookiejar = cookiejar_from_dict(cookies_dict)

# 测试 API
print("\n=== 测试 WeRead API ===")
session = requests.Session()
session.cookies = cookiejar_from_dict(cookies_dict)

try:
    # 先访问主页面
    print("访问主页...")
    r1 = session.get("https://weread.qq.com/")
    print(f"主页状态: {r1.status_code}")
    
    # 然后尝试获取书架
    print("获取书架...")
    r = session.get(
        "https://i.weread.qq.com/shelf/sync?synckey=0&teenmode=0&album=1&onlyBookid=0"
    )
    print(f"书架状态: {r.status_code}")
    print(f"响应: {r.text[:200]}")
    
    if r.ok:
        data = r.json()
        books = data.get("books", [])
        print(f"✓ 成功! 找到 {len(books)} 本书")
    else:
        print(f"✗ 错误: {r.text}")
        
except Exception as e:
    print(f"✗ 异常: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
