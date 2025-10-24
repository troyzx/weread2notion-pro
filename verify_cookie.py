#!/usr/bin/env python3
"""
验证 WeRead Cookie 状态
"""
import os
from dotenv import load_dotenv
import requests
from requests.utils import cookiejar_from_dict
import json

load_dotenv()

cookie_str = os.getenv("WEREAD_COOKIE")

cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        if key:
            cookies_dict[key] = value

session = requests.Session()
session.cookies = cookiejar_from_dict(cookies_dict)

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}
session.headers.update(headers)

print("=== WeRead Cookie 验证 ===\n")

# 尝试不同的端点
endpoints = [
    ("书架", "https://i.weread.qq.com/shelf/sync?synckey=0"),
    ("用户信息", "https://i.weread.qq.com/user/info"),
    ("笔记本", "https://i.weread.qq.com/user/notebooks"),
]

for name, url in endpoints:
    try:
        print(f"测试 {name}: {url[:50]}...")
        r = session.get(url, timeout=5)
        print(f"  状态: {r.status_code}")
        
        if r.ok:
            print(f"  ✓ 成功")
        else:
            try:
                data = r.json()
                errcode = data.get('errcode', 'N/A')
                errmsg = data.get('errmsg', 'N/A')
                print(f"  ✗ 错误 [{errcode}]: {errmsg}")
            except:
                print(f"  ✗ 响应: {r.text[:100]}")
    except Exception as e:
        print(f"  ✗ 异常: {e}")
    print()

print("\n=== Cookie 信息 ===")
print(f"wr_skey: {cookies_dict.get('wr_skey', 'NOT SET')}")
print(f"wr_vid: {cookies_dict.get('wr_vid', 'NOT SET')}")
print(f"pac_uid: {cookies_dict.get('pac_uid', 'NOT SET')}")
