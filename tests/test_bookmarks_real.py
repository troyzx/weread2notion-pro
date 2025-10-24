#!/usr/bin/env python3
"""
测试是否能获取到真实的划线数据
"""

import sys
sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')

from weread2notionpro.weread_api import WeReadApi

api = WeReadApi()

# 获取书架
bookshelf = api.get_bookshelf()
print("=" * 80)
print("搜索有划线的书籍")
print("=" * 80)

found_bookmarks = False
for item in bookshelf['books'][:10]:
    book = item.get('book', {})
    bookmark_count = item.get('bookmarkCount', 0)
    book_id = item['bookId']
    title = book.get('title', 'Unknown')
    
    if bookmark_count > 0:
        print(f"\n书名: {title}")
        print(f"BookId: {book_id}")
        print(f"划线数: {bookmark_count}")
        
        # 获取划线
        print(f"正在获取划线...")
        bookmarks = api.get_bookmark_list(book_id)
        
        if bookmarks:
            found_bookmarks = True
            print(f"✅ 成功获取 {len(bookmarks)} 条划线!")
            
            # 打印前 3 条
            for i, bm in enumerate(bookmarks[:3]):
                print(f"\n  划线 {i+1}:")
                print(f"    标记文本: {bm.get('markText', '')[:50]}")
                print(f"    颜色: {bm.get('colorStyle', '')}")
                print(f"    创建时间: {bm.get('createTime', '')}")
        else:
            print(f"❌ 虽然显示有 {bookmark_count} 条划线，但获取返回空")

if not found_bookmarks:
    print("\n没有找到有划线的书籍")

print("\n" + "=" * 80)
