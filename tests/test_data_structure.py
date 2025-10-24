#!/usr/bin/env python3
"""
检查 query_all 返回的数据结构
"""
import sys
import traceback
import json
from dotenv import load_dotenv

from weread2notionpro.notion_helper import NotionHelper

# 加载环境变量
load_dotenv()


def inspect_data_structure():
    """检查 query_all 返回的数据结构"""
    try:
        print("初始化 NotionHelper...")
        helper = NotionHelper()
        print("✓ 初始化成功\n")

        print("调用 query_all 获取原始数据...")
        if helper.book_database_id:
            results = helper.query_all(helper.book_database_id)
            print(f"✓ 获取了 {len(results)} 条记录\n")

            if results:
                print("第一条记录的结构:")
                first_result = results[0]
                print(json.dumps(
                    {
                        "id": first_result.get("id"),
                        "type": first_result.get("type"),
                        "properties_keys": list(
                            first_result.get("properties", {}).keys()
                        ),
                    },
                    indent=2,
                    ensure_ascii=False
                ))

                print("\n'BookId' 属性的值:")
                book_id_prop = first_result.get("properties", {}).get("BookId")
                print(json.dumps(book_id_prop, indent=2, ensure_ascii=False))

                print("\n'豆瓣短评' 属性的值:")
                comment_prop = first_result.get("properties", {}).get("豆瓣短评")
                print(json.dumps(comment_prop, indent=2, ensure_ascii=False))

                print("\n✅ 数据结构检查完成")
                return True
        else:
            print("⚠️  没有找到书架数据库")
            return False

    except (Exception, KeyError) as e:
        print(f"\n✗ 错误: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = inspect_data_structure()
    sys.exit(0 if success else 1)
