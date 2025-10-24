#!/usr/bin/env python3
"""
诊断脚本：检查划线（Bookmark）和笔记（Review）的获取情况
"""

import os
import sys
import json

sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')
os.chdir('/Users/troy/Git/weread2notion-pro')

from dotenv import load_dotenv
load_dotenv()

from weread2notionpro.weread_api import WeReadApi
from weread2notionpro.notion_helper import NotionHelper


def test_notebook_list():
    """测试获取笔记本列表"""
    print("\n" + "=" * 70)
    print("📚 测试 1: 获取笔记本列表")
    print("=" * 70)
    
    try:
        weread_api = WeReadApi()
        notebooks = weread_api.get_notebooklist()
        
        if not notebooks:
            print("❌ 笔记本列表为空")
            return []
        
        print(f"✅ 成功获取 {len(notebooks)} 本笔记本")
        
        # 显示前 3 本
        for i, nb in enumerate(notebooks[:3]):
            book_id = nb.get("bookId", "N/A")
            title = nb.get("book", {}).get("title", "N/A")
            sort = nb.get("sort", "N/A")
            print(f"   [{i+1}] {title} (BookId: {book_id}, Sort: {sort})")
        
        if len(notebooks) > 3:
            print(f"   ... 还有 {len(notebooks) - 3} 本")
        
        return notebooks
    
    except Exception as e:
        print(f"❌ 获取笔记本列表失败: {e}")
        return []


def test_bookmark_list(book_id, title=""):
    """测试获取划线列表"""
    print("\n" + "=" * 70)
    print(f"🔖 测试 2: 获取划线列表 (BookId: {book_id})")
    if title:
        print(f"   书名: {title}")
    print("=" * 70)
    
    try:
        weread_api = WeReadApi()
        bookmarks = weread_api.get_bookmark_list(book_id)
        
        if not bookmarks:
            print("⚠️  没有获取到划线")
            return []
        
        print(f"✅ 成功获取 {len(bookmarks)} 条划线")
        
        # 显示前 3 条
        for i, bm in enumerate(bookmarks[:3]):
            mark_text = bm.get("markText", "N/A")[:50]
            print(f"   [{i+1}] {mark_text}...")
        
        if len(bookmarks) > 3:
            print(f"   ... 还有 {len(bookmarks) - 3} 条")
        
        return bookmarks
    
    except Exception as e:
        print(f"❌ 获取划线失败: {e}")
        return []


def test_review_list(book_id, title=""):
    """测试获取书评/笔记列表"""
    print("\n" + "=" * 70)
    print(f"📝 测试 3: 获取书评/笔记列表 (BookId: {book_id})")
    if title:
        print(f"   书名: {title}")
    print("=" * 70)
    
    try:
        weread_api = WeReadApi()
        reviews = weread_api.get_review_list(book_id)
        
        if not reviews:
            print("⚠️  没有获取到书评/笔记")
            return []
        
        print(f"✅ 成功获取 {len(reviews)} 条书评/笔记")
        
        # 显示前 3 条
        for i, rv in enumerate(reviews[:3]):
            content = rv.get("content", "N/A")[:50]
            print(f"   [{i+1}] {content}...")
        
        if len(reviews) > 3:
            print(f"   ... 还有 {len(reviews) - 3} 条")
        
        return reviews
    
    except Exception as e:
        print(f"❌ 获取书评/笔记失败: {e}")
        return []


def test_chapter_info(book_id, title=""):
    """测试获取章节信息"""
    print("\n" + "=" * 70)
    print(f"📖 测试 4: 获取章节信息 (BookId: {book_id})")
    if title:
        print(f"   书名: {title}")
    print("=" * 70)
    
    try:
        weread_api = WeReadApi()
        chapters = weread_api.get_chapter_info(book_id)
        
        if not chapters:
            print("⚠️  没有获取到章节信息")
            return None
        
        print(f"✅ 成功获取章节信息")
        print(f"   共 {len(chapters)} 个章节")
        
        # 显示前 3 个
        for i, ch in enumerate(chapters[:3]):
            title = ch.get("title", "N/A")
            print(f"   [{i+1}] {title}")
        
        if len(chapters) > 3:
            print(f"   ... 还有 {len(chapters) - 3} 个")
        
        return chapters
    
    except Exception as e:
        print(f"❌ 获取章节信息失败: {e}")
        return None


def test_notion_book_data():
    """测试 Notion 中的书籍数据"""
    print("\n" + "=" * 70)
    print("📌 测试 5: Notion 中的书籍数据")
    print("=" * 70)
    
    try:
        notion_helper = NotionHelper()
        notion_books = notion_helper.get_all_book()
        
        if not notion_books:
            print("❌ Notion 中没有书籍数据")
            return {}
        
        print(f"✅ Notion 中有 {len(notion_books)} 本书籍")
        
        # 显示前 3 本
        for i, (book_id, book_info) in enumerate(list(notion_books.items())[:3]):
            print(f"   [{i+1}] BookId: {book_id}")
            print(f"       Sort: {book_info.get('Sort')}")
        
        if len(notion_books) > 3:
            print(f"   ... 还有 {len(notion_books) - 3} 本")
        
        return notion_books
    
    except Exception as e:
        print(f"❌ 获取 Notion 书籍数据失败: {e}")
        return {}


def main():
    """主函数"""
    print("\n🚀 划线和笔记获取诊断工具")
    print("用于检查为什么划线和笔记没有正常获取")
    
    # 测试 1: 获取笔记本列表
    notebooks = test_notebook_list()
    
    if not notebooks:
        print("\n❌ 无法获取笔记本列表，请检查 Cookie 和网络连接")
        return
    
    # 测试 5: 获取 Notion 书籍数据
    notion_books = test_notion_book_data()
    
    # 选择一本书进行详细测试
    test_book_id = None
    test_book_title = None
    
    # 优先选择在 Notion 中存在的书
    for nb in notebooks:
        book_id = nb.get("bookId")
        if book_id in notion_books:
            test_book_id = book_id
            test_book_title = nb.get("book", {}).get("title", "Unknown")
            break
    
    # 如果没找到，就选择第一本
    if not test_book_id and notebooks:
        test_book_id = notebooks[0].get("bookId")
        test_book_title = notebooks[0].get("book", {}).get("title", "Unknown")
    
    if not test_book_id:
        print("\n❌ 没有可用的书籍进行测试")
        return
    
    print(f"\n🎯 选择 《{test_book_title}》 (BookId: {test_book_id}) 进行详细测试")
    
    # 测试 2: 获取划线
    bookmarks = test_bookmark_list(test_book_id, test_book_title)
    
    # 测试 3: 获取书评/笔记
    reviews = test_review_list(test_book_id, test_book_title)
    
    # 测试 4: 获取章节信息
    chapters = test_chapter_info(test_book_id, test_book_title)
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 诊断总结")
    print("=" * 70)
    
    summary = {
        "笔记本列表": f"✅ {len(notebooks)} 本" if notebooks else "❌ 为空",
        "Notion 书籍": f"✅ {len(notion_books)} 本" if notion_books else "❌ 为空",
        "划线列表": f"✅ {len(bookmarks)} 条" if bookmarks else "⚠️  为空",
        "书评/笔记": f"✅ {len(reviews)} 条" if reviews else "⚠️  为空",
        "章节信息": f"✅ {len(chapters)} 个" if chapters else "⚠️  为空",
    }
    
    for key, value in summary.items():
        print(f"  {key:15} : {value}")
    
    # 建议
    print("\n💡 建议:")
    
    if not bookmarks and reviews:
        print("  • 划线为空但笔记有数据 - 可能是划线同步的 API 问题")
    elif bookmarks and not reviews:
        print("  • 笔记为空但划线有数据 - 可能是笔记同步的 API 问题")
    elif not bookmarks and not reviews:
        print("  • 划线和笔记都为空 - 检查:")
        print("    1. WeChat Reading 中是否真的有划线和笔记")
        print("    2. Cookie 是否仍然有效")
        print("    3. 网络连接是否正常")
    else:
        print("  • 数据获取正常，请检查 Notion 数据库配置是否正确")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
