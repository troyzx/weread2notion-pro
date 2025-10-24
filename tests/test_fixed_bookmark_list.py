#!/usr/bin/env python3
"""
测试修复后的 get_bookmark_list 函数
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread import get_bookmark_list
from weread2notionpro.weread_api import WeReadApi


def test_get_bookmark_list():
    """测试 get_bookmark_list 函数"""
    print("=" * 80)
    print("测试修复后的 get_bookmark_list 函数")
    print("=" * 80)
    print()

    try:
        # 获取书架，找一本测试书
        api = WeReadApi()
        bookshelf = api.get_bookshelf()
        books = bookshelf.get("books", [])

        if not books:
            print("❌ 书架为空，无法测试")
            return

        # 选择第一本书进行测试
        test_book = books[0]
        book_id = test_book.get("bookId")
        book_title = test_book.get("book", {}).get("title", "未知")

        print(f"测试书籍: {book_title}")
        print(f"BookId: {book_id}")
        print()

        # 测试 get_bookmark_list 函数
        # 注意：这里需要一个有效的 page_id，但我们只是测试 API 调用部分
        # 所以传入一个假的 page_id 也没关系，因为我们只关心 API 调用
        fake_page_id = "test_page_id"
        print("调用 get_bookmark_list 函数...")
        bookmarks = get_bookmark_list(fake_page_id, book_id)

        print(f"✅ 函数返回 {len(bookmarks)} 条划线")
        if bookmarks:
            print("划线示例:")
            for i, bookmark in enumerate(bookmarks[:2], 1):
                mark_text = bookmark.get("markText", "")[:50]
                print(f"  {i}. {mark_text}...")
        print()

    except Exception as e:  # noqa: BLE001
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_get_bookmark_list()