#!/usr/bin/env python3
"""
测试两种 Session 方案
"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

# === 方案 A: 单一 session，直接获取 ===
print("=" * 80)
print("方案 A: 单一持久 Session，直接获取 /api/user/notebook")
print("=" * 80)
session_a = requests.Session()
session_a.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})
session_a.cookies.update(cookies_dict)

r = session_a.get('https://weread.qq.com/api/user/notebook')
data = r.json()
if 'books' in data and len(data['books']) > 0:
    book_id = data['books'][0]['bookId']
    print(f"✅ 获取笔记本成功，首本书: {book_id}")
    
    # 尝试获取划线
    r2 = session_a.get('https://weread.qq.com/web/book/bookmarklist', params={'bookId': book_id})
    data2 = r2.json()
    if data2.get('errCode'):
        print(f"❌ 获取划线失败: errCode={data2.get('errCode')}, errMsg={data2.get('errMsg')}")
    else:
        print(f"✅ 获取划线成功")

print()

# === 方案 B: 模拟 weread_api.py 的逻辑（先访问主页） ===
print("=" * 80)
print("方案 B: 先访问主页，再访问 /api/user/notebook")
print("=" * 80)
session_b = requests.Session()
session_b.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})
session_b.cookies.update(cookies_dict)

# Step 1: 访问主页
print("Step 1: 访问主页...")
r = session_b.get('https://weread.qq.com/')
print(f"  状态码: {r.status_code}")

# Step 2: 访问笔记本API
print("Step 2: 访问笔记本API...")
r = session_b.get('https://weread.qq.com/api/user/notebook')
print(f"  状态码: {r.status_code}")
data = r.json()
if 'books' in data and len(data['books']) > 0:
    book_id = data['books'][0]['bookId']
    print(f"  ✅ 获取笔记本成功，首本书: {book_id}")
    
    # Step 3: 获取划线
    print(f"Step 3: 获取划线...")
    r2 = session_b.get('https://weread.qq.com/web/book/bookmarklist', params={'bookId': book_id})
    data2 = r2.json()
    if data2.get('errCode'):
        print(f"  ❌ 获取划线失败: errCode={data2.get('errCode')}, errMsg={data2.get('errMsg')}")
    else:
        print(f"  ✅ 获取划线成功")

print()
print("=" * 80)
