#!/usr/bin/env python3
"""
找一本有笔记的书来验证
"""

import sys
sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')

from weread2notionpro.weread_api import WeReadApi

# 创建 API 实例
api = WeReadApi()

# 获取书架
bookshelf = api.get_bookshelf()
if bookshelf.get('books'):
    print("=" * 80)
    print("寻找有笔记的书")
    print("=" * 80)
    
    for item in bookshelf['books'][:5]:  # 检查前 5 本
        book = item.get('book', {})
        note_count = item.get('noteCount', 0)
        bookmark_count = item.get('bookmarkCount', 0)
        book_id = item['bookId']
        title = book.get('title', 'Unknown')
        
        print(f"\n书名: {title}")
        print(f"BookId: {book_id}")
        print(f"笔记数: {note_count}, 划线数: {bookmark_count}")
        
        if note_count > 0 or bookmark_count > 0:
            print("✅ 发现有笔记或划线的书!")
            
            # 获取划线
            print(f"\n获取划线...")
            bookmarks = api.get_bookmark_list(book_id)
            print(f"✅ 获取到 {len(bookmarks)} 条划线")
            
            # 获取笔记
            print(f"获取笔记...")
            reviews = api.get_review_list(book_id)
            print(f"✅ 获取到 {len(reviews)} 条笔记")
            
            if bookmarks:
                print(f"\n第一条划线示例:")
                print(f"  {bookmarks[0]}")
            
            if reviews:
                print(f"\n第一条笔记示例:")
                print(f"  {reviews[0]}")
            
            break

print("\n" + "=" * 80)
