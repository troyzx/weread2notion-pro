#!/usr/bin/env python3
"""
直接发送 API 请求，输出完整的返回值
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')
os.chdir('/Users/troy/Git/weread2notion-pro')

load_dotenv()

WEREAD_COOKIE = os.getenv("WEREAD_COOKIE")
WEREAD_URL = "https://weread.qq.com/"

def parse_cookie():
    cookies_dict = {}
    cookie_pairs = WEREAD_COOKIE.split(';')
    for pair in cookie_pairs:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key:
                cookies_dict[key] = value
    return cookies_dict

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
    }

cookies_dict = parse_cookie()
headers = get_headers()
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies_dict)

# 获取笔记本列表
print("=" * 80)
print("[1] GET /api/user/notebook")
print("=" * 80)
resp1 = session.get(WEREAD_URL + "api/user/notebook", timeout=10)
print(f"状态码: {resp1.status_code}\n")
data1 = resp1.json()
print(json.dumps(data1, ensure_ascii=False, indent=2))

if data1.get('books'):
    book_id = data1['books'][0]['bookId']
    print(f"\n使用第一本书进行后续测试: BookId = {book_id}\n")
    
    # 测试 /web/book/bookmarklist
    print("=" * 80)
    print(f"[2] GET /web/book/bookmarklist?bookId={book_id}")
    print("=" * 80)
    resp2 = session.get(
        WEREAD_URL + "web/book/bookmarklist",
        params={"bookId": book_id},
        timeout=10
    )
    print(f"状态码: {resp2.status_code}\n")
    data2 = resp2.json()
    print(json.dumps(data2, ensure_ascii=False, indent=2))
    
    # 测试 /web/review/list
    print("\n" + "=" * 80)
    print(f"[3] GET /web/review/list?bookId={book_id}&listType=11&mine=1&syncKey=0")
    print("=" * 80)
    resp3 = session.get(
        WEREAD_URL + "web/review/list",
        params={"bookId": book_id, "listType": 11, "mine": 1, "syncKey": 0},
        timeout=10
    )
    print(f"状态码: {resp3.status_code}\n")
    data3 = resp3.json()
    print(json.dumps(data3, ensure_ascii=False, indent=2))
    
    # 测试 /web/book/chapterInfos
    print("\n" + "=" * 80)
    print(f"[4] POST /web/book/chapterInfos with bookId={book_id}")
    print("=" * 80)
    resp4 = session.post(
        WEREAD_URL + "web/book/chapterInfos",
        json={"bookIds": [book_id], "synckeys": [0], "teenmode": 0},
        timeout=10
    )
    print(f"状态码: {resp4.status_code}\n")
    data4 = resp4.json()
    print(json.dumps(data4, ensure_ascii=False, indent=2))
    
    # 测试其他可能的端点
    print("\n" + "=" * 80)
    print(f"[5] GET /web/readinfo?bookId={book_id}")
    print("=" * 80)
    try:
        resp5 = session.get(
            WEREAD_URL + "web/readinfo",
            params={"bookId": book_id},
            timeout=10
        )
        print(f"状态码: {resp5.status_code}\n")
        data5 = resp5.json()
        print(json.dumps(data5, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试 /web/book/getProgress
    print("\n" + "=" * 80)
    print(f"[6] GET /web/book/getProgress?bookId={book_id}")
    print("=" * 80)
    try:
        resp6 = session.get(
            WEREAD_URL + "web/book/getProgress",
            params={"bookId": book_id},
            timeout=10
        )
        print(f"状态码: {resp6.status_code}\n")
        data6 = resp6.json()
        print(json.dumps(data6, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试 /web/book/info
    print("\n" + "=" * 80)
    print(f"[7] GET /web/book/info?bookId={book_id}")
    print("=" * 80)
    try:
        resp7 = session.get(
            WEREAD_URL + "web/book/info",
            params={"bookId": book_id},
            timeout=10
        )
        print(f"状态码: {resp7.status_code}\n")
        data7 = resp7.json()
        print(json.dumps(data7, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 80)
