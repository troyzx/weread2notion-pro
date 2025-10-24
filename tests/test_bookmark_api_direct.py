#!/usr/bin/env python3
"""
直接测试 bookmark API 调用
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weread2notionpro.weread_api import WeReadApi


def test_bookmark_api_directly():
    """直接测试 bookmark API 调用"""
    print("=" * 80)
    print("直接测试 bookmark API 调用")
    print("=" * 80)
    print()

    try:
        # 获取书架，找一本测试书
        api = WeReadApi()
        bookshelf = api.get_bookshelf()
        books = bookshelf.get("books", [])

        if not books:
            print("❌ 书架为空，无法测试")
            return

        # 选择第一本书进行测试
        test_book = books[0]
        book_id = test_book.get("bookId")
        book_title = test_book.get("book", {}).get("title", "未知")

        print(f"测试书籍: {book_title}")
        print(f"BookId: {book_id}")
        print()

        # 直接模拟 get_bookmark_list 中的 API 调用逻辑
        print("执行 API 调用流程...")

        # 步骤 1: 刷新 session
        api.session.get("https://weread.qq.com/")
        api.session.get("https://weread.qq.com/api/user/notebook")

        # 步骤 2: 请求 bookmarklist
        url = "https://weread.qq.com/web/book/bookmarklist"
        params = {"bookId": book_id}
        response = api.session.get(url, params=params)

        # 检查响应状态
        if not response.ok:
            print(f"❌ bookmarklist API 请求失败: HTTP {response.status_code}")
            return

        # 解析 JSON 响应
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"❌ bookmarklist API 返回非 JSON 响应: {response.text[:200]}")
            return

        # 检查错误代码
        if data.get("errCode") == -2012:
            print("❌ bookmarklist API 返回 -2012 (登录超时)")
            return
        elif data.get("errCode") and data.get("errCode") != 0:
            print(f"❌ bookmarklist API 返回错误: {data.get('errCode')}")
            return

        # 提取划线列表
        bookmarks = data.get("updated", [])
        print(f"✅ API 调用成功，获取到 {len(bookmarks)} 条划线")

        if bookmarks:
            print("划线示例:")
            for i, bookmark in enumerate(bookmarks[:2], 1):
                mark_text = bookmark.get("markText", "")[:50]
                chapter = bookmark.get("chapterName", "")
                print(f"  {i}. [{chapter}] {mark_text}...")

    except Exception as e:  # noqa: BLE001
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_bookmark_api_directly()