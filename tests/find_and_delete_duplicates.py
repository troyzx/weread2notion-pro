#!/usr/bin/env python3
"""
检查并删除 Notion 书架数据库中的重复项
重复指的是具有相同 BookId 的多条记录
"""

import os
import sys

sys.path.insert(0, '/Users/troy/Git/weread2notion-pro')
os.chdir('/Users/troy/Git/weread2notion-pro')

from dotenv import load_dotenv
load_dotenv()

from weread2notionpro.notion_helper import NotionHelper
from weread2notionpro.utils import get_property_value

def find_duplicates():
    """找出所有重复的书籍"""
    notion_helper = NotionHelper()
    
    print("\n" + "=" * 70)
    print("🔍 检查 Notion 书架数据库中的重复项...")
    print("=" * 70)
    
    if not notion_helper.book_database_id:
        print("❌ 无法找到书架数据库")
        return []
    
    # 获取所有书籍
    results = notion_helper.query_all(notion_helper.book_database_id)
    print(f"\n📚 从数据库中获取 {len(results)} 条记录")
    
    # 按 BookId 分组
    books_by_id = {}
    for result in results:
        try:
            properties = result.get("properties", {})
            book_id = get_property_value(properties.get("BookId"))
            page_id = result.get("id")
            title = get_property_value(properties.get("书名"))
            
            if not book_id:
                print(f"⚠️  记录 {page_id} 没有 BookId，跳过")
                continue
            
            if book_id not in books_by_id:
                books_by_id[book_id] = []
            
            books_by_id[book_id].append({
                "page_id": page_id,
                "title": title,
                "cover": result.get("cover"),
                "created_time": result.get("created_time"),
            })
        except Exception as e:
            print(f"⚠️  处理记录时出错: {e}")
            continue
    
    # 找出重复项
    duplicates = {k: v for k, v in books_by_id.items() if len(v) > 1}
    
    if not duplicates:
        print("\n✅ 没有找到重复项！")
        return []
    
    print(f"\n⚠️  找到 {len(duplicates)} 个重复的 BookId")
    print("-" * 70)
    
    duplicate_pages = []
    for book_id, pages in duplicates.items():
        print(f"\n📖 BookId: {book_id}")
        print(f"   书名: {pages[0].get('title', 'N/A')}")
        print(f"   重复数量: {len(pages)} 条记录")
        
        # 按创建时间排序，保留最新的，删除旧的
        sorted_pages = sorted(pages, key=lambda x: x['created_time'], reverse=True)
        
        for idx, page in enumerate(sorted_pages):
            status = "✅ 保留" if idx == 0 else "🗑️  删除"
            created = page['created_time'][:10]
            print(f"   {status} - {page['page_id']} (创建于: {created})")
            
            if idx > 0:  # 除了第一个（最新的）外的都要删除
                duplicate_pages.append({
                    "page_id": page['page_id'],
                    "book_id": book_id,
                    "title": page['title'],
                    "reason": f"重复（保留时间最晚的）"
                })
    
    return duplicate_pages


def delete_duplicates(duplicate_pages, dry_run=True):
    """删除重复的页面"""
    if not duplicate_pages:
        print("\n✅ 没有需要删除的页面")
        return 0
    
    notion_helper = NotionHelper()
    
    print("\n" + "=" * 70)
    if dry_run:
        print(f"🔍 演练模式：将要删除 {len(duplicate_pages)} 个重复页面")
    else:
        print(f"🗑️  准备删除 {len(duplicate_pages)} 个重复页面")
    print("=" * 70)
    
    deleted_count = 0
    
    for page_info in duplicate_pages:
        page_id = page_info['page_id']
        book_id = page_info['book_id']
        title = page_info['title']
        
        if dry_run:
            print(f"  [{deleted_count + 1}] 将删除: {title} (ID: {book_id})")
            print(f"      Page ID: {page_id}")
            deleted_count += 1
        else:
            try:
                notion_helper.client.pages.update(page_id=page_id, archived=True)
                print(f"  ✅ 已归档: {title} (ID: {book_id})")
                print(f"     Page ID: {page_id}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {title}")
                print(f"     错误: {e}")
    
    return deleted_count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检查并删除 Notion 中的重复页面')
    parser.add_argument(
        '--execute',
        action='store_true',
        help='实际删除重复项（默认为演练模式）'
    )
    
    args = parser.parse_args()
    dry_run = not args.execute
    
    print("\n🚀 Notion 重复项检查和删除工具")
    
    # 第一步：查找重复
    duplicate_pages = find_duplicates()
    
    if not duplicate_pages:
        print("\n✨ 没有需要处理的重复项，工作完成！")
        return
    
    # 第二步：删除重复
    deleted = delete_duplicates(duplicate_pages, dry_run=dry_run)
    
    print("\n" + "=" * 70)
    if dry_run:
        print(f"✅ 演练完成，共发现 {deleted} 个重复页面需要删除")
        print("\n💡 使用以下命令实际删除重复项:")
        print("   python find_and_delete_duplicates.py --execute")
    else:
        print(f"✨ 删除完成，共删除 {deleted} 个重复页面")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
