import pendulum
from weread2notionpro.notion_helper import NotionHelper
from weread2notionpro.weread_api import WeReadApi
from weread2notionpro import utils
from weread2notionpro.config import book_properties_type_dict, tz

TAG_ICON_URL = "https://www.notion.so/icons/tag_gray.svg"
USER_ICON_URL = "https://www.notion.so/icons/user-circle-filled_gray.svg"
BOOK_ICON_URL = "https://www.notion.so/icons/book_gray.svg"
rating = {"poor": "⭐️", "fair": "⭐️⭐️⭐️", "good": "⭐️⭐️⭐️⭐️⭐️"}



def insert_book_to_notion(books, index, bookId):
    """插入Book到Notion"""
    book = {}
    if bookId in archive_dict:
        book["书架分类"] = archive_dict.get(bookId)
    if bookId in notion_books:
        book.update(notion_books.get(bookId))
    bookInfo = weread_api.get_bookinfo(bookId)
    if bookInfo != None:
        book.update(bookInfo)
    readInfo = weread_api.get_read_info(bookId)
    # 研究了下这个状态不知道什么情况有的虽然读了状态还是1 markedStatus = 1 想读 4 读完 其他为在读
    readInfo.update(readInfo.get("readDetail", {}))
    readInfo.update(readInfo.get("bookInfo", {}))
    book.update(readInfo)
    book["阅读进度"] = (
        100 if (book.get("markedStatus") == 4) else book.get("readingProgress", 0)
    ) / 100
    markedStatus = book.get("markedStatus")
    status = "想读"
    if markedStatus == 4:
        status = "已读"
    elif book.get("readingTime", 0) >= 60:
        status = "在读"
    book["阅读状态"] = status
    book["阅读时长"] = book.get("readingTime")
    book["阅读天数"] = book.get("totalReadDay")
    book["评分"] = book.get("newRating")
    if book.get("newRatingDetail") and book.get("newRatingDetail").get("myRating"):
        book["我的评分"] = rating.get(book.get("newRatingDetail").get("myRating"))
    elif status == "已读":
        book["我的评分"] = "未评分"
    book["时间"] = (
        book.get("finishedDate")
        or book.get("lastReadingDate")
        or book.get("readingBookDate")
    )
    book["开始阅读时间"] = book.get("beginReadingDate")
    book["最后阅读时间"] = book.get("lastReadingDate")
    cover = book.get("cover").replace("/s_", "/t7_")
    if not cover or not cover.strip() or not cover.startswith("http"):
        cover = BOOK_ICON_URL
    if bookId not in notion_books:
        book["书名"] = book.get("title")
        book["BookId"] = book.get("bookId")
        book["ISBN"] = book.get("isbn")
        book["链接"] = weread_api.get_url(bookId)
        book["简介"] = book.get("intro")
        book["作者"] = [
            notion_helper.get_relation_id(
                x, notion_helper.author_database_id, USER_ICON_URL
            )
            for x in book.get("author").split(" ")
        ]
        if book.get("categories"):
            book["分类"] = [
                notion_helper.get_relation_id(
                    x.get("title"), notion_helper.category_database_id, TAG_ICON_URL
                )
                for x in book.get("categories")
            ]
    properties = utils.get_properties(book, book_properties_type_dict)
    if book.get("时间"):
        notion_helper.get_date_relation(
            properties,
            pendulum.from_timestamp(book.get("时间"), tz="Asia/Shanghai"),
        )

    print(
        f"正在插入《{book.get('title')}》,一共{len(books)}本，当前是第{index+1}本。"
    )
    parent = {"database_id": notion_helper.book_database_id, "type": "database_id"}
    result = None
    if bookId in notion_books:
        result = notion_helper.update_page(
            page_id=notion_books.get(bookId).get("pageId"),
            properties=properties,
            cover=utils.get_icon(cover),
        )
    else:
        result = notion_helper.create_book_page(
            parent=parent,
            properties=properties,
            icon=utils.get_icon(cover),
        )
    page_id = result.get("id")
    if book.get("readDetail") and book.get("readDetail").get("data"):
        data = book.get("readDetail").get("data")
        data = {item.get("readDate"): item.get("readTime") for item in data}
        insert_read_data(page_id, data)


def insert_read_data(page_id, readTimes):
    readTimes = dict(sorted(readTimes.items()))
    filter = {"property": "书架", "relation": {"contains": page_id}}
    results = notion_helper.query_all_by_book(notion_helper.read_database_id, filter)
    for result in results:
        timestamp = result.get("properties").get("时间戳").get("number")
        duration = result.get("properties").get("时长").get("number")
        id = result.get("id")
        if timestamp in readTimes:
            value = readTimes.pop(timestamp)
            if value != duration:
                insert_to_notion(
                    page_id=id,
                    timestamp=timestamp,
                    duration=value,
                    book_database_id=page_id,
                )
    for key, value in readTimes.items():
        insert_to_notion(None, int(key), value, page_id)


def insert_to_notion(page_id, timestamp, duration, book_database_id):
    parent = {"database_id": notion_helper.read_database_id, "type": "database_id"}
    properties = {
        "标题": utils.get_title(
            pendulum.from_timestamp(timestamp, tz=tz).to_date_string()
        ),
        "日期": utils.get_date(
            start=pendulum.from_timestamp(timestamp, tz=tz).format(
                "YYYY-MM-DD HH:mm:ss"
            )
        ),
        "时长": utils.get_number(duration),
        "时间戳": utils.get_number(timestamp),
        "书架": utils.get_relation([book_database_id]),
    }
    if page_id != None:
        notion_helper.client.pages.update(page_id=page_id, properties=properties)
    else:
        notion_helper.client.pages.create(
            parent=parent,
            icon=utils.get_icon("https://www.notion.so/icons/target_red.svg"),
            properties=properties,
        )


weread_api = WeReadApi()
notion_helper = NotionHelper()
archive_dict = {}
notion_books = {}


def main():
    global notion_books
    global archive_dict
    
    print("=" * 60)
    print("开始微信读书同步任务")
    print("=" * 60)
    
    print("\n[1/5] 获取书架数据...")
    bookshelf_books = weread_api.get_bookshelf()
    print("✓ 获取到书架数据")
    
    print("\n[2/5] 获取已有的 Notion 书籍...")
    try:
        notion_books = notion_helper.get_all_book()
        print(f"✓ Notion 中已有 {len(notion_books)} 本书籍")
    except Exception as e:
        print(f"⚠️  获取 Notion 书籍失败: {e}")
        print("   将使用直接查询方法来检查重复")
        notion_books = {}
    
    bookProgress = bookshelf_books.get("bookProgress")
    bookProgress = {book.get("bookId"): book for book in bookProgress}
    
    for archive in bookshelf_books.get("archive"):
        name = archive.get("name")
        bookIds = archive.get("bookIds")
        archive_dict.update({bookId: name for bookId in bookIds})
    
    not_need_sync = []
    for key, value in notion_books.items():
        if (
            (
                key not in bookProgress
                or value.get("readingTime")
                == bookProgress.get(key).get("readingTime")
            )
            and (archive_dict.get(key) == value.get("category"))
            and (value.get("cover") is not None)
            and (
                value.get("status") != "已读"
                or (value.get("status") == "已读"
                    and value.get("myRating"))
            )
        ):
            not_need_sync.append(key)
    
    print(f"✓ 检测到 {len(not_need_sync)} 本书籍无需更新")
    
    print("\n[3/5] 获取笔记本列表...")
    notebooks = weread_api.get_notebooklist()
    notebooks = [d["bookId"] for d in notebooks if "bookId" in d]
    print(f"✓ 获取到 {len(notebooks)} 本笔记本")
    
    print("\n[4/5] 获取书架书籍列表...")
    books = bookshelf_books.get("books")
    books = [d["bookId"] for d in books if "bookId" in d]
    print(f"✓ 获取到 {len(books)} 本书架书籍")
    
    # 合并笔记本和书架书籍
    all_book_ids = list((set(notebooks) | set(books)))
    
    # 防止重复: 当 notion_books 无法获取时，使用直接查询
    print("\n[5/5] 检查重复书籍...")
    if not notion_books and len(all_book_ids) > 0:
        print("⚠️  Notion 书籍信息无法获取，使用直接查询方法...")
        try:
            existing_book_ids = notion_helper.check_existing_books(
                all_book_ids
            )
            if existing_book_ids:
                not_need_sync.extend(existing_book_ids)
                print(f"✓ 检测到 {len(existing_book_ids)} 本已有书籍，"
                      "跳过重复同步")
                sample = existing_book_ids[:5]
                suffix = "..." if len(existing_book_ids) > 5 else ""
                print(f"   已有: {sample}{suffix}")
        except (Exception, ValueError) as e:
            print(f"⚠️  直接查询也失败: {e}")
            print("   将继续同步所有书籍，但可能产生重复")
    else:
        print(f"✓ 正常检查完成，无需更新 {len(not_need_sync)} 本")
    
    # 去除不需要同步的书籍
    books_to_sync = list(set(all_book_ids) - set(not_need_sync))
    print(f"\n总共需要同步: {len(books_to_sync)} 本书籍")
    print(f"  (笔记本: {len(notebooks)} + 书架: {len(books)} "
          f"- 无需更新: {len(not_need_sync)})")
    
    if len(books_to_sync) > 0:
        print("\n" + "=" * 60)
        print("开始插入/更新书籍")
        print("=" * 60)
        for index, bookId in enumerate(books_to_sync):
            insert_book_to_notion(books_to_sync, index, bookId)
        print("\n" + "=" * 60)
        print("✓ 同步完成")
        print("=" * 60)
    else:
        print("\n✓ 所有书籍都是最新的，无需同步")


if __name__ == "__main__":
    main()
