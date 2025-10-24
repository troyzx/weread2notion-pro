#!/usr/bin/env python3
"""
测试 query_all 方法是否能正确处理多数据源数据库
"""
import sys
import traceback
from dotenv import load_dotenv

from weread2notionpro.notion_helper import NotionHelper

# 加载环境变量
load_dotenv()


def test_query_all():
    """测试 query_all 方法"""
    try:
        print("初始化 NotionHelper...")
        helper = NotionHelper()

        print("✓ 初始化成功")
        print(f"  书架数据库 ID: {helper.book_database_id}")

        print("\n测试 query_all 方法...")
        if helper.book_database_id:
            books = helper.query_all(helper.book_database_id)
            print(f"✓ 成功获取 {len(books)} 本书籍")
            if books:
                first_book = books[0]
                print(f"  第一本书: {first_book.get('id')}")
        else:
            print("⚠️  没有找到书架数据库")

        return True
    except (Exception, KeyError) as e:
        print(f"✗ 错误: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_query_all()
    sys.exit(0 if success else 1)
