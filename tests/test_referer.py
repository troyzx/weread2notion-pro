#!/usr/bin/env python3
"""
测试 Referer 是否是关键
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

tests = [
    ('1. 仅 User-Agent', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }),
    ('2. UA + Content-Type', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json',
    }),
    ('3. UA + Referer', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Referer': 'https://weread.qq.com/',
    }),
    ('4. UA + Content-Type + Referer', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json',
        'Referer': 'https://weread.qq.com/',
    }),
    ('5. 完整 UA + Referer', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://weread.qq.com/',
    }),
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
