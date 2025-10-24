#!/usr/bin/env python3
import requests
import os
import sys

os.chdir('/Users/troy/Git/weread2notion-pro')

from dotenv import load_dotenv
load_dotenv()

cookies_dict = {}
for pair in os.getenv('WEREAD_COOKIE', '').split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

# 尝试几个不同的端点
endpoints = [
    'https://i.weread.qq.com/user/notebooks',
    'https://weread.qq.com/web/user/notebooks', 
    'https://weread.qq.com/api/user/notebooks',
    'https://i.weread.qq.com/user/noteBooks',
]

print("尝试找到笔记本 API 端点:\n")

for url in endpoints:
    try:
        resp = requests.get(url, headers=headers, cookies=cookies_dict, timeout=3)
        data = resp.json()
        
        if 'errcode' in data and data['errcode'] != 0:
            print(f'✗ {url}')
            print(f'   errcode: {data["errcode"]} - {data.get("errmsg", "")}')
        else:
            print(f'✓ {url}')
            if 'books' in data:
                print(f'   Found {len(data["books"])} books')
            else:
                keys = list(data.keys())
                print(f'   Keys: {keys[:5]}')
    except Exception as e:
        print(f'✗ {url}')
        print(f'   Error: {str(e)[:60]}')
