#!/usr/bin/env python3
"""
测试不同的 WeRead API 端点
"""
import os
import requests
from requests.utils import cookiejar_from_dict
from dotenv import load_dotenv

load_dotenv()

WEREAD_COOKIE = os.getenv("WEREAD_COOKIE")

def parse_cookie():
    """解析 Cookie 字符串"""
    cookies_dict = {}
    cookie_pairs = WEREAD_COOKIE.split(';')
    
    for pair in cookie_pairs:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            if key:
                cookies_dict[key] = value
    
    return cookies_dict

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.103 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
    }

print("=" * 70)
print("测试不同的 WeRead API 端点")
print("=" * 70)

cookies_dict = parse_cookie()
headers = get_headers()

# 测试 1: /api/user/notebook (obsidian-weread-plugin 使用)
print("\n1. 测试 /api/user/notebook (obsidian 方式):")
try:
    resp = requests.get(
        "https://weread.qq.com/api/user/notebook",
        headers=headers,
        cookies=cookies_dict,
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:300]}...")
    
    # 检查 set-cookie 头
    if 'set-cookie' in resp.headers or 'Set-Cookie' in resp.headers:
        cookie_header = resp.headers.get('set-cookie') or resp.headers.get('Set-Cookie')
        print(f"   ✓ 收到 set-cookie: {cookie_header[:100]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("errcode") == 0:
            print(f"   ✓ 成功! 书籍数: {len(data.get('books', []))}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 2: /web/book/info (obsidian 用来获取书籍详情)
print("\n2. 测试 /web/book/info (需要 bookId):")
try:
    resp = requests.get(
        "https://weread.qq.com/web/book/info?bookId=1000000",
        headers=headers,
        cookies=cookies_dict,
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:300]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   响应: {data}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 3: 先调用主页获取 set-cookie，然后再获取书架
print("\n3. 测试：先访问主页获取 set-cookie (刷新 session)")
try:
    # 首先访问主页
    resp1 = requests.get(
        "https://weread.qq.com/",
        headers=headers,
        cookies=cookies_dict,
        timeout=10
    )
    print(f"   主页访问: {resp1.status_code}")
    
    # 检查是否返回了新的 cookie
    if 'set-cookie' in resp1.headers or 'Set-Cookie' in resp1.headers:
        cookie_header = resp1.headers.get('set-cookie') or resp1.headers.get('Set-Cookie')
        print(f"   ✓ 收到 set-cookie: {cookie_header[:80]}...")
        
        # 解析新的 cookie
        # 这里简化处理，实际应该使用 set-cookie-parser
        # 但这里先尝试直接使用返回的 cookie
    
    # 然后调用 /api/user/notebook
    resp2 = requests.get(
        "https://weread.qq.com/api/user/notebook",
        headers=headers,
        cookies=cookies_dict,
        allow_redirects=True,
        timeout=10
    )
    print(f"   获取书架: {resp2.status_code}")
    print(f"   响应体: {resp2.text[:300]}...")
    
    if resp2.status_code == 200:
        data = resp2.json()
        if data.get("errcode") == 0:
            print(f"   ✓ 成功! 书籍数: {len(data.get('books', []))}")
        else:
            print(f"   ✗ 错误: {data}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print("\n" + "=" * 70)
