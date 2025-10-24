#!/usr/bin/env python3
"""
看看 API 直接返回什么
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

session = requests.Session()
session.cookies.update(cookies_dict)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://weread.qq.com/',
})

# 获取笔记本
r = session.get('https://weread.qq.com/api/user/notebook')
data = r.json()
book_id = data['books'][0]['bookId']
print(f"首本书: {book_id}, 笔记数: {data['books'][0].get('noteCount', 0)}\n")

# 直接获取笔记列表
print("=" * 80)
print("获取笔记列表的原始响应")
print("=" * 80)
r2 = session.get('https://weread.qq.com/web/review/list',
                 params={'bookId': book_id, 'listType': 11, 'mine': 1, 'syncKey': 0})
data2 = r2.json()
print(json.dumps(data2, ensure_ascii=False, indent=2))
