#!/usr/bin/env python3
"""
找到有笔记的书并测试获取笔记
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread_api import WeReadApi


def find_and_test_books_with_notes():
    """查找有笔记的书并测试"""
    
    print("=" * 80)
    print("查找有笔记的书籍并测试获取笔记")
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
        
        # 查找有笔记的书
        books_with_notes = []
        for book in books:
            note_count = book.get("book", {}).get("noteCount", 0)
            if note_count > 0:
                books_with_notes.append(book)
        
        print(f"找到 {len(books_with_notes)} 本有笔记的书:")
        print()
        
        if not books_with_notes:
            print("⚠️  没有找到有笔记的书")
            return
        
        # 测试每本有笔记的书
        for idx, book in enumerate(books_with_notes[:5], 1):  # 测试前 5 本
            book_id = book.get("bookId")
            book_title = book.get("book", {}).get("title", "未知")
            note_count = book.get("book", {}).get("noteCount", 0)
            
            print(f"{idx}. 书名: {book_title}")
            print(f"   BookId: {book_id}")
            print(f"   笔记数: {note_count}")
            
            # 获取笔记
            try:
                reviews = api.get_review_list(book_id)
                print(f"   ✅ 获取到 {len(reviews)} 条笔记")
                
                # 显示前 2 条笔记的内容
                if reviews:
                    for i, review in enumerate(reviews[:2], 1):
                        content = review.get("content", "")[:60]
                        print(f"      {i}. {content}...")
            except Exception as e:  # noqa: BLE001
                print(f"   ❌ 获取失败: {e}")
            
            print()
        
    except Exception as e:  # noqa: BLE001
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_and_test_books_with_notes()
