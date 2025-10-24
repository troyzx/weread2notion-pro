#!/usr/bin/env python3
import requests
from dotenv import load_dotenv
import os

load_dotenv()

cookies_dict = {}
for pair in os.getenv('WEREAD_COOKIE').split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        if key:
            cookies_dict[key] = value

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

print("=" * 80)
print("测试 WeRead API 端点")
print("=" * 80)

# 测试各个端点
endpoints = [
    ('书架 /api/user/notebook', 'https://weread.qq.com/api/user/notebook'),
    ('笔记本 /user/notebooks', 'https://i.weread.qq.com/user/notebooks'),
]

for name, url in endpoints:
    try:
        print(f"\n{name}")
        print(f"  URL: {url}")
        resp = requests.get(url, headers=headers, cookies=cookies_dict, timeout=5)
        print(f"  Status: {resp.status_code}")
        
        data = resp.json()
        errcode = data.get('errcode', None)
        
        if errcode is None:
            # 正常响应
            keys = list(data.keys())[:5]
            print(f"  响应字段: {keys}")
            print(f"  ✓ 成功")
        else:
            print(f"  errcode: {errcode}")
            print(f"  errmsg: {data.get('errmsg', 'N/A')}")
            if errcode == -2012:
                print(f"  ✗ Cookie 认证失败")
            else:
                print(f"  ✗ 错误")
    except Exception as e:
        print(f"  ✗ 错误: {e}")

print("\n" + "=" * 80)
