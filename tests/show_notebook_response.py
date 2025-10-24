#!/usr/bin/env python3
"""
获取 /api/user/notebook 的完整返回结果
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})

r = session.get('https://weread.qq.com/api/user/notebook', timeout=10)
data = r.json()

print(json.dumps(data, ensure_ascii=False, indent=2))
