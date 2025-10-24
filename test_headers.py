#!/usr/bin/env python3
"""
测试带有完整请求头的 WeRead API
"""
import os
from dotenv import load_dotenv
import requests
from requests.utils import cookiejar_from_dict

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

# 添加完整的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://weread.qq.com',
    'Referer': 'https://weread.qq.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}

# 测试 API
print("=== 带完整请求头的 WeRead API 测试 ===")
session = requests.Session()
session.cookies = cookiejar_from_dict(cookies_dict)
session.headers.update(headers)

try:
    # 先访问主页面
    print("1. 访问主页...")
    r1 = session.get("https://weread.qq.com/")
    print(f"   状态: {r1.status_code}")
    
    # 然后尝试获取书架
    print("2. 获取书架...")
    r = session.get(
        "https://i.weread.qq.com/shelf/sync?synckey=0&teenmode=0&album=1&onlyBookid=0"
    )
    print(f"   状态: {r.status_code}")
    
    if r.ok:
        data = r.json()
        books = data.get("books", [])
        print(f"   ✓ 成功! 找到 {len(books)} 本书")
        if books:
            for i, book in enumerate(books[:3]):
                print(f"     {i+1}. {book.get('title', 'N/A')}")
    else:
        resp_json = r.json()
        errcode = resp_json.get('errcode')
        errmsg = resp_json.get('errmsg')
        print(f"   ✗ 错误 [{errcode}]: {errmsg}")
        print(f"   完整响应: {r.text}")
        
except Exception as e:
    print(f"✗ 异常: {type(e).__name__}: {e}")
