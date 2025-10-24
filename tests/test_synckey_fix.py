#!/usr/bin/env python3
"""
测试 synckey 参数修正
根据最新的 WeChat Reading API 文档，参数应该是 synckey（小写）
而不是 syncKey（驼峰）
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread_api import WeReadApi


def test_review_list_with_synckey_fix():
    """测试带有 synckey 修正的笔记列表获取"""
    
    print("=" * 80)
    print("测试：synckey 参数修正")
    print("=" * 80)
    print()
    
    try:
        api = WeReadApi()
        
        # 获取书架列表
        print("步骤 1: 获取书架列表...")
        bookshelf = api.get_bookshelf()
        books = bookshelf.get("books", [])
        print(f"✅ 获取到 {len(books)} 本书")
        print()
        
        if not books:
            print("❌ 书架为空，无法测试")
            return
        
        # 找第一本有笔记的书
        test_book = None
        for book in books:
            if book.get("book", {}).get("noteCount", 0) > 0:
                test_book = book
                break
        
        if not test_book:
            print("⚠️  未找到有笔记的书，使用第一本书进行测试")
            test_book = books[0]
        
        book_id = test_book.get("bookId")
        book_title = test_book.get("book", {}).get("title", "未知")
        note_count = test_book.get("book", {}).get("noteCount", 0)
        
        print(f"步骤 2: 测试书籍 - {book_title}")
        print(f"  BookId: {book_id}")
        print(f"  笔记数: {note_count}")
        print()
        
        # 尝试获取笔记列表
        print("步骤 3: 获取笔记列表（使用 synckey 小写参数）...")
        reviews = api.get_review_list(book_id)
        
        if reviews:
            print(f"✅ 成功！获取到 {len(reviews)} 条笔记")
            print()
            print("笔记示例:")
            for i, review in enumerate(reviews[:3], 1):
                print(f"  {i}. {review.get('content', '')[:50]}...")
        else:
            print("❌ 获取失败，返回空列表")
        print()
        
    except Exception as e:  # noqa: BLE001
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_review_list_with_synckey_fix()
