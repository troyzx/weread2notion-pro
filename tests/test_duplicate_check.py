#!/usr/bin/env python3
"""
测试书籍重复问题和解决方案
"""
import sys
import traceback
from dotenv import load_dotenv

from weread2notionpro.notion_helper import NotionHelper
from weread2notionpro.weread_api import WeReadApi

# 加载环境变量
load_dotenv()


def test_duplicate_issue():
    """测试书籍重复的问题"""
    try:
        print("=" * 60)
        print("测试书籍重复问题诊断")
        print("=" * 60)

        print("\n初始化...")
        helper = NotionHelper()
        weread_api = WeReadApi()
        print("✓ 初始化成功\n")

        # 步骤 1: 获取书架数据
        print("[步骤 1] 获取书架数据...")
        bookshelf = weread_api.get_bookshelf()
        books_from_api = bookshelf.get("books", [])
        book_ids = [d["bookId"] for d in books_from_api if "bookId" in d]
        print(f"✓ API 返回 {len(book_ids)} 本书籍")

        # 步骤 2: 获取 Notion 中的书籍
        print("\n[步骤 2] 获取 Notion 中的书籍...")
        try:
            notion_books = helper.get_all_book()
            print(f"✓ Notion 中已有 {len(notion_books)} 本书籍")
            if len(notion_books) > 0:
                sample_book_id = list(notion_books.keys())[0]
                print(f"  样本: {sample_book_id}")
        except Exception as e:
            print(f"✗ 获取 Notion 书籍失败: {e}")
            notion_books = {}

        # 步骤 3: 检查重复
        print("\n[步骤 3] 检查重复...")
        if not notion_books and len(book_ids) > 0:
            print("⚠️  Notion 书籍为空，尝试直接检查...")
            existing = helper.check_existing_books(book_ids[:10])
            print(f"✓ 直接检查前10本书籍: {len(existing)} 本已存在")
            if existing:
                print(f"  已存在的书籍: {existing[:5]}")
        else:
            print(f"✓ 可以正常检查重复")

        # 步骤 4: 模拟同步逻辑
        print("\n[步骤 4] 模拟同步逻辑...")
        not_need_sync = []
        if notion_books:
            # 正常情况
            for key in notion_books:
                if key in book_ids:
                    not_need_sync.append(key)
            print(f"✓ 从 Notion 数据检查: {len(not_need_sync)} 本无需更新")
        else:
            # 异常情况 - 使用直接检查
            existing_ids = helper.check_existing_books(book_ids)
            not_need_sync.extend(existing_ids)
            print(f"✓ 使用直接检查: {len(existing_ids)} 本已存在")

        # 步骤 5: 显示最终结果
        print("\n[步骤 5] 最终统计...")
        to_sync = len(book_ids) - len(not_need_sync)
        print(f"  API 书籍总数: {len(book_ids)}")
        print(f"  需要跳过: {len(not_need_sync)}")
        print(f"  需要同步: {to_sync}")

        print("\n" + "=" * 60)
        print("✅ 诊断完成")
        print("=" * 60)
        return True

    except (Exception, KeyError) as e:
        print(f"\n✗ 错误: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_duplicate_issue()
    sys.exit(0 if success else 1)
