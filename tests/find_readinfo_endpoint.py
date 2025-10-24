#!/usr/bin/env python3
import requests
import os
import sys

sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')
os.chdir('/Users/troy/Git/weread2notion-pro')

from dotenv import load_dotenv
load_dotenv()

cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
bookId = '3300129525'
params = {'bookId': bookId}

endpoints = [
    'https://weread.qq.com/web/api/book/readinfo',
    'https://weread.qq.com/book/readinfo',
    'https://i.weread.qq.com/book/readinfo',
]

print("寻找有效的 readinfo 端点:")
for url in endpoints:
    try:
        resp = requests.get(url, headers=headers, cookies=cookies_dict, params=params, timeout=2)
        print(f"{url:50} → {resp.status_code}", end="")
        if resp.status_code == 200:
            data = resp.json()
            if data.get('errcode') is None or data.get('errcode') == 0:
                print(" ✅")
            else:
                print(f" (errcode: {data.get('errcode')})")
        else:
            print()
    except Exception as e:
        print(f"{url:50} → 错误")
