#!/usr/bin/env python3
"""
调试划线 API 的返回值
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
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Referer': 'https://weread.qq.com/',
})

# 访问主页
session.get('https://weread.qq.com/')

# 获取笔记本
r = session.get('https://weread.qq.com/api/user/notebook')
data = r.json()

# 找有划线的书
for item in data['books'][:5]:
    if item.get('bookmarkCount', 0) > 0:
        book_id = item['bookId']
        title = item['book']['title']
        print(f"测试书: {title} (BookId: {book_id}, 划线数: {item['bookmarkCount']})\n")
        
        # 获取划线
        r2 = session.get('https://weread.qq.com/web/book/bookmarklist',
                         params={'bookId': book_id})
        data2 = r2.json()
        
        print("=" * 80)
        print("原始响应:")
        print("=" * 80)
        print(json.dumps(data2, ensure_ascii=False, indent=2))
        break
