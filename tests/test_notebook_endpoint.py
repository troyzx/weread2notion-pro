#!/usr/bin/env python3
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# 获取 cookie
cookie_str = os.getenv('WEREAD_COOKIE', '')
print(f"Cookie: {cookie_str[:50]}...")

# 方式 1：使用 Cookie 头
print("\n=== 方式 1: 使用 Cookie 头 ===")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://weread.qq.com/',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': cookie_str,
}

try:
    resp = requests.post(
        'https://i.weread.qq.com/user/notebooks',
        headers=headers,
        timeout=3
    )
    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
except Exception as e:
    print(f"错误: {e}")

# 方式 2：使用 Session 管理 Cookie
print("\n=== 方式 2: 使用 Session ===")
session = requests.Session()
# 手动设置 Cookie
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        session.cookies.set(key.strip(), value.strip())

headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://weread.qq.com/',
    'X-Requested-With': 'XMLHttpRequest',
}

try:
    resp = session.post(
        'https://i.weread.qq.com/user/notebooks',
        headers=headers2,
        timeout=3
    )
    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
except Exception as e:
    print(f"错误: {e}")

# 方式 3：测试 /api/user/notebook 是否包含笔记本信息
print("\n=== 方式 3: 检查 /api/user/notebook 返回的字段 ===")
try:
    headers3 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    cookies_dict = {}
    for pair in cookie_str.split(';'):
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies_dict[key.strip()] = value.strip()
    
    resp = requests.get('https://weread.qq.com/api/user/notebook', headers=headers3, cookies=cookies_dict, timeout=3)
    data = resp.json()
    
    # 检查响应结构
    print(f"顶层字段: {list(data.keys())}")
    if 'books' in data and data['books']:
        first_book = data['books'][0]
        print(f"第一本书的字段: {list(first_book.keys())}")
        
        # 检查是否有 notebook 相关的字段
        notebook_fields = [k for k in first_book.keys() if 'note' in k.lower()]
        if notebook_fields:
            print(f"Notebook 相关字段: {notebook_fields}")
            for field in notebook_fields:
                print(f"  {field}: {first_book[field]}")
    
except Exception as e:
    print(f"错误: {e}")
