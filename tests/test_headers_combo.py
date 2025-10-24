#!/usr/bin/env python3
"""
测试是否需要特定的 Referer 或其他请求头
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

# === 尝试不同的请求头组合 ===

# 组合 1: 最小请求头
print("=" * 80)
print("组合 1: 最小请求头")
print("=" * 80)
s1 = requests.Session()
s1.cookies.update(cookies_dict)
s1.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})
r1 = s1.get('https://weread.qq.com/web/book/bookmarklist',
            params={'bookId': book_id})
d1 = r1.json()
print("结果: " + str(d1.get('errCode', 'OK')) + "\n")

# 组合 2: 添加完整的浏览器请求头
print("=" * 80)
print("组合 2: 完整的浏览器请求头")
print("=" * 80)
s2 = requests.Session()
s2.cookies.update(cookies_dict)
s2.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Referer': 'https://weread.qq.com/',
})
r2 = s2.get('https://weread.qq.com/web/book/bookmarklist',
            params={'bookId': book_id})
d2 = r2.json()
print("结果: " + str(d2.get('errCode', 'OK')) + "\n")

# 组合 3: 先访问主页再获取
print("=" * 80)
print("组合 3: 先访问主页，建立 session 状态")
print("=" * 80)
s3 = requests.Session()
s3.cookies.update(cookies_dict)
s3.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
})
# 访问主页
s3.get('https://weread.qq.com/')
# 访问笔记本
s3.get('https://weread.qq.com/api/user/notebook')
# 获取划线
r3 = s3.get('https://weread.qq.com/web/book/bookmarklist',
            params={'bookId': book_id})
d3 = r3.json()
print("结果: " + str(d3.get('errCode', 'OK')) + "\n")

print("=" * 80)
