#!/usr/bin/env python3
"""
测试修复后的 weread_api 是否能获取划线和笔记
"""

import sys
sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')

from weread2notionpro.weread_api import WeReadApi

# 创建 API 实例
api = WeReadApi()

# 获取书架
print("=" * 80)
print("获取书架")
print("=" * 80)
bookshelf = api.get_bookshelf()
if bookshelf.get('books'):
    book_id = bookshelf['books'][0]['bookId']
    print(f"✅ 获取书架成功，首本书: {book_id}\n")
    
    # 获取划线
    print("=" * 80)
    print(f"获取划线 (BookId: {book_id})")
    print("=" * 80)
    bookmarks = api.get_bookmark_list(book_id)
    print(f"✅ 获取划线成功，数量: {len(bookmarks)}\n")
    
    # 获取笔记
    print("=" * 80)
    print(f"获取笔记 (BookId: {book_id})")
    print("=" * 80)
    reviews = api.get_review_list(book_id)
    print(f"✅ 获取笔记成功，数量: {len(reviews)}\n")
    
    # 获取章节
    print("=" * 80)
    print(f"获取章节 (BookId: {book_id})")
    print("=" * 80)
    chapters = api.get_chapter_info(book_id)
    print(f"✅ 获取章节成功，数量: {len(chapters)}\n")
else:
    print("❌ 获取书架失败")

print("=" * 80)
