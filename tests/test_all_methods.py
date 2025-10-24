#!/usr/bin/env python3
"""
测试 query 和 query_all 方法
"""
import sys
import traceback
from dotenv import load_dotenv

from weread2notionpro.notion_helper import NotionHelper

# 加载环境变量
load_dotenv()


def test_methods():
    """测试各种查询方法"""
    try:
        print("初始化 NotionHelper...")
        helper = NotionHelper()
        print("✓ 初始化成功\n")

        # 测试 query_all
        print("测试 query_all 方法...")
        if helper.book_database_id:
            books = helper.query_all(helper.book_database_id)
            print(f"✓ query_all 成功: 获取 {len(books)} 本书籍")
        else:
            print("⚠️  没有找到书架数据库")

        # 测试 query (带过滤)
        print("\n测试 query 方法 (带过滤)...")
        if helper.setting_database_id:
            result = helper.query(
                database_id=helper.setting_database_id,
                filter={"property": "标题", "title": {"equals": "设置"}}
            )
            pages = result.get("results", [])
            print(f"✓ query 成功: 获取 {len(pages)} 条设置记录")
            if pages:
                title = pages[0].get("properties", {}).get("标题", {})
                print(f"  标题: {title}")
        else:
            print("⚠️  没有找到设置数据库")

        # 测试 get_all_book
        print("\n测试 get_all_book 方法...")
        all_books = helper.get_all_book()
        print(f"✓ get_all_book 成功: 获取 {len(all_books)} 本书籍的信息")
        if all_books:
            first_book_id = list(all_books.keys())[0]
            first_book = all_books[first_book_id]
            print(f"  第一本书 ID: {first_book_id}")
            print(f"  页面 ID: {first_book.get('pageId', 'N/A')}")
            print(f"  阅读状态: {first_book.get('status', 'N/A')}")

        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        return True

    except (Exception, KeyError) as e:
        print(f"\n✗ 错误: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_methods()
    sys.exit(0 if success else 1)
