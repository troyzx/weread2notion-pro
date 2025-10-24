#!/usr/bin/env python3
"""
测试 ObsidianWeRead 插件的 API 调用方式
参考: https://github.com/ObsidianWeRead/obsidian-weread
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
    }

print("\n" + "=" * 70)
print("🔍 ObsidianWeRead 插件 API 调用方式测试")
print("=" * 70)

cookies_dict = parse_cookie()
headers = get_headers()
session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies_dict)

# 首先获取书籍列表
print("\n[1] 获取笔记本列表...")
try:
    resp = session.get(WEREAD_URL + "api/user/notebook", timeout=10)
    print(f"    状态码: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        books = data.get('books', [])
        print(f"    ✅ 成功获取 {len(books)} 本笔记本")
        
        if books:
            book = books[0]
            book_id = book.get('bookId')
            book_title = book.get('book', {}).get('title', 'Unknown')
            print(f"\n    第一本书: {book_title} (ID: {book_id})")
            
            # 现在尝试获取这本书的划线
            print(f"\n[2] 尝试 ObsidianWeRead 的方式获取划线...")
            print(f"    方式 A: POST /web/book/getMarks (推荐)")
            
            # 这是 obsidian-weread 插件使用的方式
            try:
                body = {
                    "bookId": book_id,
                    "listType": None,
                    "syncKey": 0,
                    "isAll": False
                }
                resp_marks = session.post(
                    WEREAD_URL + "web/book/getMarks",
                    json=body,
                    timeout=10
                )
                print(f"    状态码: {resp_marks.status_code}")
                if resp_marks.status_code == 200:
                    marks_data = resp_marks.json()
                    print(f"    响应: {json.dumps(marks_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    if marks_data.get('errCode') == 0:
                        items = marks_data.get('items', [])
                        print(f"    ✅ 成功获取 {len(items)} 条划线")
                    else:
                        print(f"    ❌ 错误: {marks_data.get('errMsg')}")
                else:
                    print(f"    ❌ HTTP 错误: {resp_marks.status_code}")
                    print(f"    响应: {resp_marks.text[:200]}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")
            
            # 尝试其他方式
            print(f"\n    方式 B: GET /web/book/bookmarklist")
            try:
                resp_old = session.get(
                    WEREAD_URL + "web/book/bookmarklist",
                    params={"bookId": book_id},
                    timeout=10
                )
                print(f"    状态码: {resp_old.status_code}")
                if resp_old.status_code == 200:
                    old_data = resp_old.json()
                    print(f"    响应: {json.dumps(old_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    if 'updated' in old_data:
                        print(f"    ✅ 获取到 {len(old_data.get('updated', []))} 条划线")
                    else:
                        print(f"    ❌ 格式错误，没有 'updated' 字段")
                else:
                    print(f"    ❌ HTTP 错误: {resp_old.status_code}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")
            
            # 尝试获取书评
            print(f"\n[3] 尝试获取书评/笔记...")
            print(f"    方式 A: POST /web/book/getReviews")
            
            try:
                body = {
                    "bookId": book_id,
                    "listType": 11,
                    "syncKey": 0,
                    "isAll": False
                }
                resp_reviews = session.post(
                    WEREAD_URL + "web/book/getReviews",
                    json=body,
                    timeout=10
                )
                print(f"    状态码: {resp_reviews.status_code}")
                if resp_reviews.status_code == 200:
                    reviews_data = resp_reviews.json()
                    print(f"    响应: {json.dumps(reviews_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    if reviews_data.get('errCode') == 0:
                        items = reviews_data.get('items', [])
                        print(f"    ✅ 成功获取 {len(items)} 条书评")
                    else:
                        print(f"    ❌ 错误: {reviews_data.get('errMsg')}")
                else:
                    print(f"    ❌ HTTP 错误: {resp_reviews.status_code}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")
            
            # 尝试获取章节
            print(f"\n[4] 尝试获取章节信息...")
            print(f"    方式 A: POST /web/book/chapterInfos")
            
            try:
                body = {
                    "bookIds": [book_id],
                    "synckeys": [0],
                    "teenmode": 0
                }
                resp_chapters = session.post(
                    WEREAD_URL + "web/book/chapterInfos",
                    json=body,
                    timeout=10
                )
                print(f"    状态码: {resp_chapters.status_code}")
                if resp_chapters.status_code == 200:
                    chapters_data = resp_chapters.json()
                    print(f"    响应: {json.dumps(chapters_data, ensure_ascii=False, indent=2)[:500]}")
                    
                    if 'data' in chapters_data and chapters_data.get('data'):
                        chapters = chapters_data['data'][0].get('updated', [])
                        print(f"    ✅ 成功获取 {len(chapters)} 个章节")
                    else:
                        print(f"    ❌ 格式错误")
                else:
                    print(f"    ❌ HTTP 错误: {resp_chapters.status_code}")
            except Exception as e:
                print(f"    ❌ 异常: {e}")

except Exception as e:
    print(f"    ❌ 错误: {e}")

print("\n" + "=" * 70 + "\n")
