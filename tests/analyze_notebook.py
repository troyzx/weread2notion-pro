#!/usr/bin/env python3
"""
分析 /api/user/notebook 返回的结构和内容
"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

session = requests.Session()
session.cookies.update(cookies_dict)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
})

r = session.get('https://weread.qq.com/api/user/notebook', timeout=10)
data = r.json()

print("=" * 80)
print("API: GET https://weread.qq.com/api/user/notebook")
print("=" * 80)

# 顶级结构
print("\n【顶级字段】")
print(f"  synckey: {data.get('synckey')} (用于同步)")
print(f"  totalBookCount: {data.get('totalBookCount')} (书籍总数)")
print(f"  noBookReviewCount: {data.get('noBookReviewCount')}")
print(f"  books: 数组，共 {len(data.get('books', []))} 本书")

# 每本书的字段
print("\n【books 数组中每个对象的字段】")
if data.get('books'):
    book_item = data['books'][0]
    
    print("\n顶级字段:")
    for key in book_item.keys():
        value = book_item[key]
        if isinstance(value, dict):
            print(f"  {key}: {{...}} (对象)")
        elif isinstance(value, list):
            print(f"  {key}: [...] (数组，{len(value)} 项)")
        else:
            print(f"  {key}: {value} ({type(value).__name__})")
    
    # book 对象的字段
    print("\n【book 对象内的字段】(共 {} 个)".format(len(book_item['book'])))
    book = book_item['book']
    important_fields = [
        'bookId', 'title', 'author', 'translator', 'cover', 'version',
        'format', 'price', 'categories', 'finished', 'publishTime'
    ]
    for field in important_fields:
        if field in book:
            value = book[field]
            if isinstance(value, (dict, list)):
                print(f"  {field}: {type(value).__name__}")
            else:
                print(f"  {field}: {value}")

# 显示完整的第一本书
print("\n" + "=" * 80)
print("【第一本书的完整数据】")
print("=" * 80)
print(json.dumps(data['books'][0], ensure_ascii=False, indent=2))

# 统计信息
print("\n" + "=" * 80)
print("【统计信息】")
print("=" * 80)

notes_total = sum(item.get('noteCount', 0) for item in data.get('books', []))
bookmarks_total = sum(item.get('bookmarkCount', 0) for item in data.get('books', []))
reviews_total = sum(item.get('reviewCount', 0) for item in data.get('books', []))

print(f"总笔记数: {notes_total}")
print(f"总划线数: {bookmarks_total}")
print(f"总书评数: {reviews_total}")

# 有笔记的书
books_with_notes = [item for item in data.get('books', [])
                    if item.get('noteCount', 0) > 0]
print(f"\n有笔记的书: {len(books_with_notes)} 本")
for book in books_with_notes[:3]:
    print(f"  - {book['book']['title']}: {book['noteCount']} 条笔记")

# 有划线的书
books_with_bookmarks = [item for item in data.get('books', [])
                        if item.get('bookmarkCount', 0) > 0]
print(f"\n有划线的书: {len(books_with_bookmarks)} 本")
for book in books_with_bookmarks[:3]:
    print(f"  - {book['book']['title']}: {book['bookmarkCount']} 条划线")
