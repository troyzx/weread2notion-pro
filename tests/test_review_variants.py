#!/usr/bin/env python3
"""
调查 review/list 端点
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

session = requests.Session()
session.cookies.update(cookies_dict)
r = session.get('https://weread.qq.com/api/user/notebook')
data = r.json()
book_id = data['books'][0]['bookId']
print(f"测试书 ID: {book_id}\n")

tests = [
    ('1. 仅 Referer', {
        'Referer': 'https://weread.qq.com/',
    }),
    ('2. UA + Referer', {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://weread.qq.com/',
    }),
    ('3. 完整 UA + Referer',  {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://weread.qq.com/',
    }),
    ('4. 完整请求头 + Referer', {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Referer': 'https://weread.qq.com/',
    }),
]

print("=" * 80)
for test_name, headers in tests:
    s = requests.Session()
    s.cookies.update(cookies_dict)
    s.headers.update(headers)
    
    # 先访问主页
    s.get('https://weread.qq.com/')
    
    # 再访问 review/list
    r = s.get('https://weread.qq.com/web/review/list',
              params={'bookId': book_id, 'listType': 11, 'mine': 1,
                      'syncKey': 0})
    data = r.json()
    result = "✅ OK" if not data.get('errCode') else f"❌ {data.get('errCode')}"
    print(f"{test_name}: {result}")

print("=" * 80)
