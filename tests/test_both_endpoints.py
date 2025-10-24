#!/usr/bin/env python3
"""
分别测试 bookmarklist 和 review/list
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

# 完整请求头 + Referer
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Referer': 'https://weread.qq.com/',
}

print("=" * 80)
print("测试 bookmarklist (划线)")
print("=" * 80)
s1 = requests.Session()
s1.cookies.update(cookies_dict)
s1.headers.update(headers)
r1 = s1.get('https://weread.qq.com/web/book/bookmarklist',
            params={'bookId': book_id})
d1 = r1.json()
result1 = d1.get('errCode', 'OK')
print(f"结果: {result1}\n")

print("=" * 80)
print("测试 review/list (笔记)")
print("=" * 80)
s2 = requests.Session()
s2.cookies.update(cookies_dict)
s2.headers.update(headers)
r2 = s2.get('https://weread.qq.com/web/review/list',
            params={'bookId': book_id, 'listType': 11, 'mine': 1,
                    'syncKey': 0})
d2 = r2.json()
result2 = d2.get('errCode', 'OK')
print(f"结果: {result2}\n")

print("=" * 80)
