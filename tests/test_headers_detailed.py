#!/usr/bin/env python3
"""
逐个测试请求头来找出哪个是关键
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

# 先获取第一本书的 ID
session = requests.Session()
session.cookies.update(cookies_dict)
r = session.get('https://weread.qq.com/api/user/notebook')
data = r.json()
book_id = data['books'][0]['bookId']
print(f"测试书 ID: {book_id}\n")

# 基础请求头
base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

# 完整请求头
full_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
}

# 测试各个单独的头
tests = [
    ('1. 基础 User-Agent', base_headers),
    ('2. 完整 User-Agent', {'User-Agent': full_headers['User-Agent']}),
    ('3. 完整 UA + Accept', {
        'User-Agent': full_headers['User-Agent'],
        'Accept': full_headers['Accept'],
    }),
    ('4. 完整 UA + Accept + Content-Type', {
        'User-Agent': full_headers['User-Agent'],
        'Accept': full_headers['Accept'],
        'Content-Type': full_headers['Content-Type'],
    }),
    ('5. 所有完整请求头', full_headers),
]

print("=" * 80)
for test_name, headers in tests:
    s = requests.Session()
    s.cookies.update(cookies_dict)
    s.headers.update(headers)
    r = s.get('https://weread.qq.com/web/book/bookmarklist',
              params={'bookId': book_id})
    data = r.json()
    result = "✅ OK" if not data.get('errCode') else f"❌ {data.get('errCode')}"
    print(f"{test_name}: {result}")

print("=" * 80)
