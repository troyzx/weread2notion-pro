#!/usr/bin/env python3
"""
WeRead API 端点探测和文档生成
尝试探测所有可能的 WeRead API 端点
"""

import requests
import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

cookie_str = os.getenv('WEREAD_COOKIE', '')
cookies_dict = {}
for pair in cookie_str.split(';'):
    pair = pair.strip()
    if '=' in pair:
        key, value = pair.split('=', 1)
        cookies_dict[key.strip()] = value.strip()

class WeReadAPIDiscovery:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies.update(cookies_dict)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Referer': 'https://weread.qq.com/',
        })
        self.results = []

    def test_endpoint(self, method: str, url: str, params: Dict = None,
                      json_data: Dict = None,
                      description: str = "") -> Dict[str, Any]:
        """测试一个端点"""
        try:
            if method.upper() == 'GET':
                r = self.session.get(url, params=params, timeout=5)
            elif method.upper() == 'POST':
                r = self.session.post(url, json=json_data, timeout=5)
            else:
                return None

            try:
                data = r.json()
            except:
                data = None

            result = {
                'method': method,
                'url': url,
                'params': params,
                'json_data': json_data,
                'description': description,
                'status_code': r.status_code,
                'success': r.status_code == 200,
                'response': data,
                'has_error': data and data.get('errCode') if data else False,
            }
            return result
        except Exception as e:
            return {
                'method': method,
                'url': url,
                'description': description,
                'error': str(e),
                'success': False,
            }

    def get_test_book_id(self):
        """获取一本测试书的 ID"""
        r = self.session.get('https://weread.qq.com/api/user/notebook')
        data = r.json()
        if data.get('books'):
            return data['books'][0]['bookId']
        return None

    def discover_all(self):
        """探测所有已知的端点"""
        book_id = self.get_test_book_id()
        print(f"使用测试书 ID: {book_id}\n")

        endpoints = [
            # 基础端点
            ('GET', 'https://weread.qq.com/api/user/notebook', None, None,
             '获取笔记本列表和书架'),

            # 书籍信息相关
            ('GET', 'https://weread.qq.com/web/book/info',
             {'bookId': book_id}, None,
             '获取书籍详细信息'),

            ('GET', 'https://weread.qq.com/web/book/getProgress',
             {'bookId': book_id}, None,
             '获取书籍阅读进度'),

            # 划线相关
            ('GET', 'https://weread.qq.com/web/book/bookmarklist',
             {'bookId': book_id}, None,
             '获取划线列表'),

            # 笔记/评论相关
            ('GET', 'https://weread.qq.com/web/review/list',
             {'bookId': book_id, 'listType': 11, 'mine': 1, 'syncKey': 0},
             None,
             '获取个人笔记列表'),

            ('GET', 'https://weread.qq.com/web/review/list',
             {'bookId': book_id, 'listType': 1, 'syncKey': 0},
             None,
             '获取所有笔记列表'),

            # 章节相关
            ('POST', 'https://weread.qq.com/web/book/chapterInfos',
             None,
             {'bookIds': [book_id], 'synckeys': [0], 'teenmode': 0},
             '获取章节信息'),

            # 其他可能的端点
            ('GET', 'https://weread.qq.com/web/readdata/summary',
             {'synckey': 0}, None,
             '获取阅读数据摘要'),

            ('GET', 'https://weread.qq.com/web/readdata/detail',
             {'synckey': 0}, None,
             '获取阅读数据详情'),

            # 尝试一些其他变体
            ('GET', 'https://weread.qq.com/web/shelf/sync',
             None, None,
             '获取书架同步数据'),

            ('GET', 'https://weread.qq.com/api/readinfo',
             {'bookId': book_id}, None,
             '获取阅读信息 (API 版本)'),

            ('GET', 'https://weread.qq.com/api/bookmark',
             {'bookId': book_id}, None,
             '获取划线 (API 版本)'),

            ('GET', 'https://weread.qq.com/api/review',
             {'bookId': book_id}, None,
             '获取笔记 (API 版本)'),
        ]

        for method, url, params, json_data, desc in endpoints:
            print(f"测试: {desc}")
            print(f"  {method} {url}")
            result = self.test_endpoint(method, url, params, json_data, desc)

            if result:
                if result.get('error'):
                    print(f"  ❌ 错误: {result['error']}")
                elif result.get('has_error'):
                    print(f"  ⚠️  API 错误: {result['response'].get('errCode')} - "
                          f"{result['response'].get('errMsg')}")
                elif result['status_code'] == 404:
                    print(f"  🚫 404 Not Found")
                elif result['status_code'] == 200:
                    print(f"  ✅ 成功 (200)")
                    if result['response']:
                        keys = list(result['response'].keys())[:5]
                        print(f"     返回字段: {keys}")
                else:
                    print(f"  ⚠️  状态码: {result['status_code']}")

            self.results.append(result)
            print()

    def save_results(self):
        """保存结果到文件"""
        with open('weread_api_results.json', 'w') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print("结果已保存到 weread_api_results.json")

if __name__ == '__main__':
    discovery = WeReadAPIDiscovery()
    discovery.discover_all()
    discovery.save_results()
