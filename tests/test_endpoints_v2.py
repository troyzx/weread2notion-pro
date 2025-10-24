#!/usr/bin/env python3
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

# 尝试 /noteBooks 端点（大小写不同）
endpoints = [
    '/user/notebooks',
    '/user/noteBooks',
    '/noteBooks',
    '/api/noteBooks',
]

headers_base = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
    'Referer': 'https://weread.qq.com/',
}

print('=== 测试不同端点 ===')
for endpoint in endpoints:
    for domain in ['i.weread.qq.com', 'weread.qq.com']:
        url = f'https://{domain}{endpoint}'
        try:
            resp = requests.get(url, headers=headers_base, cookies=cookies_dict, timeout=2)
            data = resp.json()
            status = resp.status_code
            errcode = data.get('errcode', 'N/A')
            print(f'{url:50} → 状态码: {status:3} errcode: {str(errcode):6}')
        except ValueError:
            print(f'{url:50} → 非 JSON 响应')
        except Exception as e:
            print(f'{url:50} → {str(e)[:20]}')
