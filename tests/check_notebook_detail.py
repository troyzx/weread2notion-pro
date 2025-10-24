#!/usr/bin/env python3
"""
检查 /api/user/notebook 返回的数据中是否已包含笔记和划线详情
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
r = session.get('https://weread.qq.com/api/user/notebook')
data = r.json()

# 找到有笔记的书
for item in data['books'][:10]:
    if item.get('noteCount', 0) > 0:
        print("=" * 80)
        print(f"找到有笔记的书: {item['book']['title']} (BookId: {item['bookId']})")
        print("=" * 80)
        print(json.dumps(item, ensure_ascii=False, indent=2))
        break
