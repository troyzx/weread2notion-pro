#!/bin/bash

# GitHub Action 本地运行脚本
# 使用方法: ./run_locally.sh [book|weread|read_time]

set -e

# 激活虚拟环境
source .venv/bin/activate

# 设置环境变量 (请从 .env 文件或 GitHub Secrets 中读取)
export NOTION_TOKEN=${NOTION_TOKEN:-"your_notion_token_here"}
export NOTION_PAGE=${NOTION_PAGE:-"your_notion_page_id_here"}
export WEREAD_COOKIE=${WEREAD_COOKIE:-"your_weread_cookie_here"}

# 可选的环境变量（注释掉的）
# export CC_URL=""
# export CC_ID=""
# export CC_PASSWORD=""
# export HEATMAP_BLOCK_ID=""

# 定义数据库名称（可选）
# export BOOK_DATABASE_NAME=""
# export AUTHOR_DATABASE_NAME=""
# export CATEGORY_DATABASE_NAME=""
# export BOOKMARK_DATABASE_NAME=""
# export REVIEW_DATABASE_NAME=""
# export CHAPTER_DATABASE_NAME=""
# export YEAR_DATABASE_NAME=""
# export WEEK_DATABASE_NAME=""
# export MONTH_DATABASE_NAME=""
# export DAY_DATABASE_NAME=""

# 默认命令
COMMAND=${1:-"book"}

echo "运行命令: $COMMAND"
echo "使用 NOTION_TOKEN: ${NOTION_TOKEN:0:20}..."
echo "使用 NOTION_PAGE: $NOTION_PAGE"

# 执行命令
case $COMMAND in
    book)
        echo "执行微信读书书籍同步..."
        book
        ;;
    weread)
        echo "执行微信读书笔记同步..."
        weread
        ;;
    read_time)
        echo "执行微信读书阅读时间热力图..."
        read_time
        ;;
    *)
        echo "未知命令: $COMMAND"
        echo "可用命令: book, weread, read_time"
        exit 1
        ;;
esac

echo "完成！"
