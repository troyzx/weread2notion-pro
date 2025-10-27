#!/usr/bin/env python3
"""
探索新的 WeRead 阅读统计 API 端点
基于已知的工作端点推测新的可能端点
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

class ReadingStatsExplorer:
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

    def test_endpoint(self, method, url, params=None, json_data=None, description=""):
        """测试端点"""
        try:
            if method.upper() == 'GET':
                r = self.session.get(url, params=params, timeout=5)
            elif method.upper() == 'POST':
                r = self.session.post(url, json=json_data, timeout=5)
            else:
                return None

            result = {
                'method': method,
                'url': url,
                'params': params,
                'json_data': json_data,
                'description': description,
                'status_code': r.status_code,
                'success': r.status_code == 200,
                'response_length': len(r.text),
            }

            # 尝试解析 JSON
            try:
                data = r.json()
                result['response'] = data
                result['is_json'] = True
                result['errCode'] = data.get('errCode') if isinstance(data, dict) else None
            except:
                result['response'] = r.text[:200] + '...' if len(r.text) > 200 else r.text
                result['is_json'] = False

            return result
        except Exception as e:
            return {
                'method': method,
                'url': url,
                'description': description,
                'error': str(e),
                'success': False,
            }

    def explore_reading_stats_endpoints(self):
        """探索可能的阅读统计端点"""
        print("🔍 探索 WeRead 阅读统计 API 端点...")
        print("=" * 80)

        # 基于已知模式推测的新端点
        candidate_endpoints = [
            # 基于 /web/readdata/ 模式的变体
            ('GET', 'https://weread.qq.com/web/readdata/stats', None, None,
             '阅读统计数据'),
            ('GET', 'https://weread.qq.com/web/readdata/summary/v2', None, None,
             '阅读摘要 V2'),
            ('GET', 'https://weread.qq.com/web/readdata/detail/v2', None, None,
             '阅读详情 V2'),

            # 基于 /api/ 模式的变体
            ('GET', 'https://weread.qq.com/api/readdata/summary', None, None,
             'API 阅读摘要'),
            ('GET', 'https://weread.qq.com/api/readdata/detail', None, None,
             'API 阅读详情'),
            ('GET', 'https://weread.qq.com/api/user/reading/stats', None, None,
             '用户阅读统计'),
            ('GET', 'https://weread.qq.com/api/user/reading/history', None, None,
             '用户阅读历史'),

            # 基于移动端 API 模式的变体
            ('GET', 'https://i.weread.qq.com/user/reading/stats', None, None,
             '移动端阅读统计'),
            ('GET', 'https://i.weread.qq.com/user/reading/summary', None, None,
             '移动端阅读摘要'),

            # 基于书架数据的变体（可能包含阅读统计）
            ('GET', 'https://weread.qq.com/api/user/notebook/stats', None, None,
             '笔记本统计'),
            ('GET', 'https://weread.qq.com/api/user/reading/progress', None, None,
             '阅读进度统计'),

            # 基于个人资料的变体
            ('GET', 'https://weread.qq.com/web/user/profile/stats', None, None,
             '用户资料统计'),
            ('GET', 'https://weread.qq.com/api/user/profile/reading', None, None,
             '用户阅读资料'),

            # 尝试不同的参数组合
            ('GET', 'https://weread.qq.com/web/readdata/summary',
             {'synckey': 0, 'type': 'daily'}, None, '每日阅读摘要'),
            ('GET', 'https://weread.qq.com/web/readdata/detail',
             {'synckey': 0, 'type': 'daily'}, None, '每日阅读详情'),

            # 基于年度报告的变体（WeRead 有年度报告功能）
            ('GET', 'https://weread.qq.com/web/annual/report', {'year': 2024}, None,
             '年度报告'),
            ('GET', 'https://weread.qq.com/api/annual/report', {'year': 2024}, None,
             'API 年度报告'),
        ]

        results = []

        # 先建立 session 状态
        print("📡 建立 session 状态...")
        self.session.get('https://weread.qq.com/')
        self.session.get('https://weread.qq.com/api/user/notebook')

        for method, url, params, json_data, desc in candidate_endpoints:
            print(f"测试: {desc}")
            print(f"  {method} {url}")
            if params:
                print(f"  参数: {params}")

            result = self.test_endpoint(method, url, params, json_data, desc)

            if result:
                if result.get('error'):
                    print(f"  ❌ 错误: {result['error']}")
                elif result['status_code'] == 404:
                    print(f"  🚫 404 Not Found")
                elif result['status_code'] == 200:
                    if result.get('is_json', False):
                        err_code = result.get('errCode')
                        if err_code is None or err_code == 0:
                            print(f"  ✅ 成功! JSON 响应 ({result['response_length']} 字符)")
                            # 检查是否包含阅读相关数据
                            response = result.get('response', {})
                            if isinstance(response, dict):
                                keys = list(response.keys())
                                print(f"     字段: {keys[:8]}{'...' if len(keys) > 8 else ''}")
                                # 检查是否包含阅读时间数据
                                if any(key in ['readTimes', 'readingTime', 'readTime', 'stats', 'data']
                                      for key in keys):
                                    print("     🎯 可能包含阅读统计数据!")
                        else:
                            print(f"  ⚠️ API 错误: {err_code}")
                    else:
                        print(f"  ✅ 成功! 非 JSON 响应 ({result['response_length']} 字符)")
                        print(f"     内容预览: {result['response'][:100]}")
                else:
                    print(f"  ⚠️ 状态码: {result['status_code']}")
            else:
                print("  ❌ 无响应")

            results.append(result)
            print()

        # 保存结果
        with open('reading_stats_exploration.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("结果已保存到 reading_stats_exploration.json")
        return results

if __name__ == '__main__':
    explorer = ReadingStatsExplorer()
    explorer.explore_reading_stats_endpoints()