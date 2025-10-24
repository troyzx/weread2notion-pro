#!/usr/bin/env python3
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

print("Step 1: 加载 Cookie")
cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

print("Step 2: 创建 Session")
s = requests.Session()
s.cookies.update(cookies_dict)
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://weread.qq.com/',
})

print("Step 3: 获取笔记本")
r = s.get('https://weread.qq.com/api/user/notebook', timeout=5)
data = r.json()
print(f"获取到 {len(data.get('books', []))} 本书")

print("Step 4: 寻找有划线的书")
for item in data.get('books', [])[:10]:
    if item.get('bookmarkCount', 0) > 0:
        bid = item['bookId']
        title = item['book']['title']
        print(f"找到: {title} (bookmarkCount: {item.get('bookmarkCount')})")
        print("Step 5: 获取划线")
        r2 = s.get('https://weread.qq.com/web/book/bookmarklist',
                   params={'bookId': bid}, timeout=5)
        resp = r2.json()
        print(f"状态码: {r2.status_code}")
        print(f"返回类型: {type(resp)}")
        print(f"返回内容: {json.dumps(resp, ensure_ascii=False, indent=2)}")
        break
