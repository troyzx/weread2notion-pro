#!/usr/bin/env python3
"""
调试 WeRead API 调用方式
"""
import os
import json
import requests
from dotenv import load_dotenv
from requests.utils import cookiejar_from_dict

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
    
    return cookiejar_from_dict(cookies_dict)

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
    }

print("=" * 60)
print("WeRead API 调试")
print("=" * 60)

# 打印 Cookie
print("\n1. Cookie 信息:")
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
            print(f"   {key}: {value[:20]}..." if len(value) > 20 else f"   {key}: {value}")

# 创建会话
session = requests.Session()
session.cookies = parse_cookie()
session.headers.update(get_headers())

# 测试 1: 访问主页
print("\n2. 测试：访问主页 (https://weread.qq.com/)")
try:
    resp = session.get("https://weread.qq.com/", timeout=10)
    print(f"   状态码: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✓ 主页访问成功")
    else:
        print(f"   响应头: {dict(resp.headers)}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 2: 获取书架（sync 方法）
print("\n3. 测试：获取书架 (shelf/sync)")
try:
    url = "https://i.weread.qq.com/shelf/sync?synckey=0&teenmode=0&album=1&onlyBookid=0"
    resp = session.get(url, timeout=10)
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:200]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("errcode") == 0:
            print(f"   ✓ 成功")
        else:
            print(f"   ✗ 返回错误: {data}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 3: 获取书架（列表方法 - 可能是新 API）
print("\n4. 测试：获取书架 (bookshelf)")
try:
    url = "https://i.weread.qq.com/user/bookshelf"
    resp = session.get(url, timeout=10)
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:200]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("errcode") == 0:
            print(f"   ✓ 成功")
        else:
            print(f"   ✗ 返回错误: {data}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 4: POST 请求获取书架
print("\n5. 测试：POST 请求获取书架")
try:
    url = "https://i.weread.qq.com/shelf/sync"
    payload = {"synckey": 0, "teenmode": 0, "album": 1, "onlyBookid": 0}
    resp = session.post(url, json=payload, timeout=10)
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:200]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("errcode") == 0:
            print(f"   ✓ 成功")
        else:
            print(f"   ✗ 返回错误: {data}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

# 测试 5: 检查 Cookie 是否生效
print("\n6. 测试：简单 GET 请求验证 Cookie")
try:
    headers = get_headers()
    cookies = parse_cookie()
    
    # 直接使用 requests 而不是 session
    resp = requests.get(
        "https://i.weread.qq.com/shelf/sync?synckey=0&teenmode=0&album=1&onlyBookid=0",
        headers=headers,
        cookies=cookies,
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应体: {resp.text[:300]}...")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print("\n" + "=" * 60)
