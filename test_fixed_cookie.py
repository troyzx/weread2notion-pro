#!/usr/bin/env python3
"""
测试修复后的 Cookie 解析
"""
import os
from dotenv import load_dotenv
import requests
from requests.utils import cookiejar_from_dict

load_dotenv()

cookie_str = os.getenv("WEREAD_COOKIE")

print("=== 修复后的 Cookie 解析 ===")
cookies_dict = {}

# 按分号分割 cookie
cookie_pairs = cookie_str.split(';')

print(f"找到 {len(cookie_pairs)} 对\n")

for pair in cookie_pairs:
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        if key:  # 只添加非空的键
            cookies_dict[key] = value
            print(f"  {key}: {value[:40]}..." if len(value) > 40 else f"  {key}: {value}")

print(f"\n总共解析了 {len(cookies_dict)} 个有效 cookie\n")

# 测试 API
print("=== 测试 WeRead API ===")
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
    
    if r.ok:
        data = r.json()
        books = data.get("books", [])
        print(f"✓ 成功! 找到 {len(books)} 本书")
        if books:
            print(f"  第一本书: {books[0].get('title', 'N/A')}")
    else:
        print(f"✗ 错误: {r.text}")
        
except Exception as e:
    print(f"✗ 异常: {type(e).__name__}: {e}")
