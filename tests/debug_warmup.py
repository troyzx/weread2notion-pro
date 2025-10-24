#!/usr/bin/env python3
"""
尝试更激进的 session 预热
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

def test_approach(name, warmup_func):
    print("=" * 80)
    print(f"方案: {name}")
    print("=" * 80)
    
    session = requests.Session()
    session.cookies.update(cookies_dict)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://weread.qq.com/',
    })
    
    # 执行预热
    warmup_func(session)
    
    # 获取笔记列表
    r = session.get('https://weread.qq.com/api/user/notebook')
    data = r.json()
    book_id = data['books'][0]['bookId']
    
    r2 = session.get('https://weread.qq.com/web/review/list',
                     params={'bookId': book_id, 'listType': 11,
                             'mine': 1, 'syncKey': 0})
    data2 = r2.json()
    
    if data2.get('errCode'):
        print(f"❌ 错误: {data2.get('errMsg')}")
    else:
        print(f"✅ 成功! 获取到 {len(data2.get('reviews', []))} 条笔记")
    
    print()

# 方案 1: 仅访问主页
def warmup_1(s):
    print("预热: 访问主页")
    s.get('https://weread.qq.com/')

# 方案 2: 访问主页 + 笔记本
def warmup_2(s):
    print("预热: 访问主页 + 笔记本")
    s.get('https://weread.qq.com/')
    s.get('https://weread.qq.com/api/user/notebook')

# 方案 3: 访问主页 + 某本书的页面 + 笔记本
def warmup_3(s):
    print("预热: 访问主页 + 书籍页面 + 笔记本")
    s.get('https://weread.qq.com/')
    # 这里需要一个有效的书籍页面，先用笔记本获取
    r = s.get('https://weread.qq.com/api/user/notebook')
    data = r.json()
    book_id = data['books'][0]['bookId']
    # 访问书籍阅读页面
    from weread2notionpro.weread_api import WeReadApi
    api = WeReadApi()
    book_str_id = api.calculate_book_str_id(book_id)
    s.get(f'https://weread.qq.com/web/reader/{book_str_id}')

test_approach("仅 Referer", warmup_1)
test_approach("Referer + 访问主页 + 笔记本", warmup_2)
# test_approach("完整预热", warmup_3)
