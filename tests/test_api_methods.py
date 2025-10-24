#!/usr/bin/env python3
"""
测试不同的 API 端点组合
参考 obsidian-weread 的实现逻辑
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
    """解析 Cookie 字符串"""
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
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
    }

print("\n" + "=" * 70)
print("🔍 测试 obsidian-weread 真实实现")
print("=" * 70)

cookies_dict = parse_cookie()
headers = get_headers()

# 使用 requests.Session 来管理 cookies 和持久化连接
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies_dict)

# 获取书籍列表
print("\n[STEP 1] 获取笔记本列表...")
try:
    resp = session.get(WEREAD_URL + "api/user/notebook", timeout=10)
    print(f"✅ 状态码: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        books = data.get('books', [])
        print(f"✅ 成功获取 {len(books)} 本笔记本\n")
        
        if books:
            book = books[0]
            book_id = book.get('bookId')
            book_title = book.get('book', {}).get('title', 'Unknown')
            print(f"选择测试: {book_title} (ID: {book_id})\n")
            
            # obsidian-weread 的实现：先访问阅读器页面来初始化 session
            print("[STEP 2] 访问阅读器页面初始化 Session...")
            try:
                reader_url = f"{WEREAD_URL}web/reader/1"  # 这会重定向到实际的书籍
                resp_reader = session.get(reader_url, allow_redirects=True, timeout=10)
                print(f"✅ 访问阅读器: {resp_reader.status_code}")
                
                # 检查 set-cookie
                if 'Set-Cookie' in resp_reader.headers:
                    print("✅ 收到新的 Cookie")
            except Exception as e:
                print(f"⚠️  阅读器访问出错 (继续): {e}")
            
            # 现在尝试调用划线 API
            print("\n[STEP 3] 获取划线...")
            
            # 尝试新的 API
            print("   尝试方式 1: /web/book/getMarks (POST)")
            try:
                # obsidian-weread 使用 POST 方式
                payload = {
                    "bookId": book_id,
                    "listType": None,
                    "syncKey": 0,
                    "isAll": True  # 获取全部
                }
                resp_marks = session.post(
                    WEREAD_URL + "web/book/getMarks",
                    json=payload,
                    timeout=10
                )
                print(f"      状态码: {resp_marks.status_code}")
                if resp_marks.status_code != 404:
                    marks_data = resp_marks.json()
                    print(f"      响应: {marks_data}")
            except Exception as e:
                print(f"      ❌ 错误: {e}")
            
            # 尝试 GET 方式
            print("\n   尝试方式 2: /web/book/bookmarklist (GET)")
            try:
                params = {"bookId": book_id}
                resp_old = session.get(
                    WEREAD_URL + "web/book/bookmarklist",
                    params=params,
                    timeout=10
                )
                print(f"      状态码: {resp_old.status_code}")
                if resp_old.status_code == 200:
                    old_data = resp_old.json()
                    print(f"      响应 keys: {list(old_data.keys())}")
                    print(f"      errCode: {old_data.get('errCode')}")
                    print(f"      updated 数量: {len(old_data.get('updated', []))}")
            except Exception as e:
                print(f"      ❌ 错误: {e}")
            
            # 尝试使用 syncKey 参数
            print("\n   尝试方式 3: /web/book/bookmarklist (GET, with syncKey)")
            try:
                params = {
                    "bookId": book_id,
                    "syncKey": 0
                }
                resp_sync = session.get(
                    WEREAD_URL + "web/book/bookmarklist",
                    params=params,
                    timeout=10
                )
                print(f"      状态码: {resp_sync.status_code}")
                if resp_sync.status_code == 200:
                    sync_data = resp_sync.json()
                    print(f"      响应 keys: {list(sync_data.keys())}")
                    print(f"      errCode: {sync_data.get('errCode')}")
                    print(f"      更新数量: {len(sync_data.get('updated', []))}")
            except Exception as e:
                print(f"      ❌ 错误: {e}")
            
            # 尝试获取书评
            print("\n[STEP 4] 获取书评/笔记...")
            print("   尝试 /web/review/list")
            try:
                params = {
                    "bookId": book_id,
                    "listType": 11,
                    "mine": 1,
                    "syncKey": 0
                }
                resp_reviews = session.get(
                    WEREAD_URL + "web/review/list",
                    params=params,
                    timeout=10
                )
                print(f"      状态码: {resp_reviews.status_code}")
                if resp_reviews.status_code == 200:
                    reviews_data = resp_reviews.json()
                    print(f"      响应 keys: {list(reviews_data.keys())}")
                    print(f"      errCode: {reviews_data.get('errCode')}")
                    reviews = reviews_data.get('reviews', [])
                    print(f"      书评数量: {len(reviews)}")
                    if reviews:
                        print(f"      第一条书评: {reviews[0]}")
            except Exception as e:
                print(f"      ❌ 错误: {e}")

except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 70 + "\n")
