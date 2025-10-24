#!/usr/bin/env python3
"""
详细调试脚本 - 查看 /web/review/list 返回的实际响应
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread_api import WeReadApi


def debug_review_list():
    """详细调试笔记列表获取"""
    
    print("=" * 80)
    print("调试：/web/review/list 实际响应")
    print("=" * 80)
    print()
    
    try:
        api = WeReadApi()
        
        # 获取书架
        print("获取书架...")
        bookshelf = api.get_bookshelf()
        books = bookshelf.get("books", [])
        print(f"✅ 获取到 {len(books)} 本书")
        print()
        
        if not books:
            print("❌ 书架为空")
            return
        
        # 选择有笔记的书或使用第一本
        test_book = None
        for book in books:
            if book.get("book", {}).get("noteCount", 0) > 0:
                test_book = book
                break
        
        if not test_book:
            test_book = books[0]
        
        book_id = test_book.get("bookId")
        book_title = test_book.get("book", {}).get("title", "未知")
        note_count = test_book.get("book", {}).get("noteCount", 0)
        
        print(f"测试书籍: {book_title}")
        print(f"  BookId: {book_id}")
        print(f"  笔记数: {note_count}")
        print()
        
        # 刷新 session（模拟 API 方法）
        print("刷新 Cookie...")
        api.session.get("https://weread.qq.com/")
        api.session.get("https://weread.qq.com/api/user/notebook")
        print()
        
        # 直接调用 API 并查看原始响应
        print("调用 /web/review/list 端点...")
        url = "https://weread.qq.com/web/review/list"
        params = {
            "bookId": book_id,
            "listType": 11,
            "mine": 1,
            "synckey": 0
        }
        
        print(f"  URL: {url}")
        print(f"  参数: {params}")
        print()
        
        response = api.session.get(url, params=params)
        
        print(f"HTTP 状态码: {response.status_code}")
        print("响应头 (关键):")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Set-Cookie: {response.headers.get('Set-Cookie', 'N/A')}")
        print()
        
        print("响应体 (JSON):")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"  [非 JSON] {response.text[:500]}")
        
        print()
        print("错误代码分析:")
        if "errCode" in data:
            print(f"  errCode: {data.get('errCode')}")
        if "errcode" in data:
            print(f"  errcode: {data.get('errcode')}")
        if data.get("errCode") == -2012:
            print("  ⚠️  -2012 表示登录超时或 Cookie 失效")
        
    except Exception as e:  # noqa: BLE001
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_review_list()
