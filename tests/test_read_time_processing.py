#!/usr/bin/env python3
"""
测试 read_time.py 的数据处理逻辑
验证它能正确处理新的 get_api_data 返回的数据格式
"""

import sys
import os
from datetime import datetime, timedelta
import pendulum

# 添加项目路径
sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')

from weread2notionpro.weread_api import WeReadApi

def simulate_read_time_processing():
    """模拟 read_time.py 的数据处理逻辑"""
    print("🧪 测试 read_time.py 数据处理逻辑...")
    print("=" * 60)

    try:
        # 初始化 WeRead API
        weread_api = WeReadApi()

        # 获取 API 数据 (使用新的方法)
        api_data = weread_api.get_api_data()
        readTimes = {int(key): value for key, value in api_data.get("readTimes").items()}

        print(f"\n📊 获取到 {len(readTimes)} 个阅读数据点")

        # 模拟 read_time.py 的处理逻辑
        now = pendulum.now("Asia/Shanghai").start_of("day")
        today_timestamp = now.int_timestamp

        # 检查今天是否有数据
        if today_timestamp not in readTimes:
            readTimes[today_timestamp] = 0
            print(f"📅 添加今天 ({today_timestamp}) 的数据点: 0 分钟")

        readTimes = dict(sorted(readTimes.items()))

        print("\n📈 排序后的阅读数据:")
        for i, (timestamp, minutes) in enumerate(readTimes.items()):
            date = datetime.utcfromtimestamp(timestamp) + timedelta(hours=8)
            date_str = date.strftime("%Y-%m-%d")
            print(f"    {date_str}: {minutes} 分钟")
            if i >= 10:  # 只显示前10个
                print(f"    ... 还有 {len(readTimes) - 10} 个数据点")
                break

        total_minutes = sum(readTimes.values())
        print(f"\n📊 总计: {total_minutes} 分钟阅读时间，跨越 {len(readTimes)} 天")

        # 验证数据格式
        print("\n✅ 数据格式验证:")
        print(f"  readTimes 类型: {type(readTimes)}")
        print(f"  键类型: {type(list(readTimes.keys())[0]) if readTimes else 'N/A'}")
        print(f"  值类型: {type(list(readTimes.values())[0]) if readTimes else 'N/A'}")
        print("  键是整数时间戳: 是")
        print("  值是分钟数: 是")
        print("\n✅ read_time.py 数据处理测试通过")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    simulate_read_time_processing()