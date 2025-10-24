#!/usr/bin/env python3
"""
完全模拟 ObsidianWeRead 的方式测试 highlights 和 reviews
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

# 完全模仿 ObsidianWeRead 的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.103 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Content-Type': 'application/json',
}

session = requests.Session()
session.cookies.update(cookies_dict)
session.headers.update(headers)

# 获取笔记本
print("=" * 80)
print("Step 1: 获取笔记本")
print("=" * 80)
r = session.get('https://weread.qq.com/api/user/notebook', timeout=10)
data = r.json()

# 找到有划线和笔记的书
for item in data.get('books', [])[:15]:
    bookId = item['bookId']
    title = item['book']['title']
    bookmark_count = item.get('bookmarkCount', 0)
    note_count = item.get('noteCount', 0)
    
    if bookmark_count > 0 or note_count > 0:
        print(f"\n测试书: {title}")
        print(f"  BookId: {bookId}")
        print(f"  划线: {bookmark_count}, 笔记: {note_count}")
        
        # 测试获取划线
        if bookmark_count > 0:
            print(f"\n  获取划线...")
            r_marks = session.get(
                'https://weread.qq.com/web/book/bookmarklist',
                params={'bookId': bookId},
                timeout=10
            )
            marks_data = r_marks.json()
            if marks_data.get('errCode'):
                print(f"    ❌ 错误: {marks_data.get('errCode')} - "
                      f"{marks_data.get('errMsg')}")
            elif 'updated' in marks_data:
                print(f"    ✅ 成功! 获取到 {len(marks_data['updated'])} 条划线")
                if marks_data['updated']:
                    print(f"       第一条: {marks_data['updated'][0].get('markText', '')[:50]}")
            else:
                print(f"    ⚠️  返回结构异常: {marks_data}")
        
        # 测试获取笔记
        if note_count > 0:
            print(f"\n  获取笔记...")
            r_reviews = session.get(
                'https://weread.qq.com/web/review/list',
                params={
                    'bookId': bookId,
                    'listType': 11,
                    'mine': 1,
                    'synckey': 0
                },
                timeout=10
            )
            reviews_data = r_reviews.json()
            if reviews_data.get('errCode'):
                print(f"    ❌ 错误: {reviews_data.get('errCode')} - "
                      f"{reviews_data.get('errMsg')}")
            elif 'reviews' in reviews_data:
                reviews = [x.get('review') for x in reviews_data['reviews']
                          if x.get('review')]
                print(f"    ✅ 成功! 获取到 {len(reviews)} 条笔记")
                if reviews:
                    print(f"       第一条: {reviews[0].get('content', '')[:50]}")
            else:
                print(f"    ⚠️  返回结构异常: {reviews_data}")
        
        # 只测试第一本有数据的书
        break

print("\n" + "=" * 80)
