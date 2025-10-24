#!/usr/bin/env python3
"""
检查 notebook API 返回的实际数据结构
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread_api import WeReadApi


def inspect_notebook_structure():
    """检查 notebook API 结构"""
    
    print("=" * 80)
    print("检查 /api/user/notebook 返回的数据结构")
    print("=" * 80)
    print()
    
    try:
        api = WeReadApi()
        
        # 获取书架
        print("获取 notebook 数据...")
        bookshelf = api.get_bookshelf()
        
        print(f"顶级键: {list(bookshelf.keys())}")
        print()
        
        books = bookshelf.get("books", [])
        print(f"书籍数: {len(books)}")
        print()
        
        if books:
            # 查看第一本书的结构
            first_book = books[0]
            print("第一本书的结构:")
            print(json.dumps(first_book, indent=2, ensure_ascii=False)[:1000])
            
    except Exception as e:  # noqa: BLE001
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    inspect_notebook_structure()
