#!/usr/bin/env python3
"""
诊断脚本 - 检查搜索数据库问题
"""
import os
import re
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
notion_page = os.getenv("NOTION_PAGE")

print(f"NOTION_TOKEN: {notion_token[:20]}..." if notion_token else "NOT SET")
print(f"NOTION_PAGE: {notion_page}\n")

if not notion_token:
    print("错误: NOTION_TOKEN 未设置")
    exit(1)

try:
    client = Client(auth=notion_token)
    
    # 提取 page_id
    match = re.search(r"[a-f0-9]{32}", notion_page)
    if match:
        page_id = match.group(0)
    else:
        page_id = notion_page
    
    print(f"提取的 page_id: {page_id}")
    print("\n尝试列出页面的子块...")
    
    response = client.blocks.children.list(block_id=page_id)
    results = response.get("results", [])
    
    print(f"找到 {len(results)} 个子块\n")
    
    database_id_dict = {}
    
    def search_blocks_recursive(block_id, depth=0):
        indent = "  " * depth
        try:
            response = client.blocks.children.list(block_id=block_id)
            children = response.get("results", [])
            
            for idx, child in enumerate(children):
                child_type = child.get("type")
                print(f"{indent}子块 {idx}: 类型={child_type}")
                
                if child_type == "child_database":
                    db_title = child.get("child_database", {}).get("title")
                    db_id = child.get("id")
                    database_id_dict[db_title] = db_id
                    print(f"{indent}  ✓ 数据库: {db_title}")
                    print(f"{indent}    ID: {db_id}")
                
                elif child_type == "embed":
                    url = child.get("embed", {}).get("url")
                    if url:
                        print(f"{indent}  链接: {url[:60]}...")
                        if url.startswith("https://heatmap.malinkang.com/"):
                            print(f"{indent}  ✓ 热力图块")
                
                # 递归搜索子块
                if child.get("has_children"):
                    print(f"{indent}  递归搜索子块...")
                    search_blocks_recursive(child.get("id"), depth + 1)
        
        except Exception as e:
            print(f"{indent}错误: {e}")
    
    # 开始递归搜索
    search_blocks_recursive(page_id)
    
    print("\n")
    
    print(f"\n\n找到的数据库:")
    for db_name, db_id in database_id_dict.items():
        print(f"  {db_name}: {db_id}")
    
    if not database_id_dict:
        print("  ⚠️  未找到任何数据库！")
    
except Exception as e:
    print(f"错误: {type(e).__name__}")
    print(f"消息: {e}")
    import traceback
    traceback.print_exc()
