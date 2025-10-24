import hashlib
import json
import os
import re

import requests
from requests.utils import cookiejar_from_dict
from retrying import retry
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
WEREAD_URL = "https://weread.qq.com/"
WEREAD_NOTEBOOKS_URL = "https://weread.qq.com/api/user/notebook"
WEREAD_BOOKMARKLIST_URL = "https://weread.qq.com/web/book/bookmarklist"
WEREAD_CHAPTER_INFO = "https://weread.qq.com/web/book/chapterInfos"
WEREAD_READ_INFO_URL = "https://weread.qq.com/web/book/readinfo"
WEREAD_REVIEW_LIST_URL = "https://weread.qq.com/web/review/list"
WEREAD_BOOK_INFO = "https://weread.qq.com/web/book/info"
WEREAD_READDATA_DETAIL = "https://weread.qq.com/web/readdata/detail"
WEREAD_HISTORY_URL = "https://weread.qq.com/web/readdata/summary?synckey=0"


class WeReadApi:
    def __init__(self):
        self.cookie = self.get_cookie()
        self.session = requests.Session()
        self.session.cookies = self.parse_cookie_string()
        # 设置标准的浏览器请求头
        self.session.headers.update(self._get_headers())

    def _get_headers(self):
        """获取标准的浏览器请求头 - 参考 ObsidianWeRead 插件"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.103 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
        }

    def try_get_cloud_cookie(self, url, id, password):
        if url.endswith("/"):
            url = url[:-1]
        req_url = f"{url}/get/{id}"
        data = {"password": password}
        result = None
        response = requests.post(req_url, data=data)
        if response.status_code == 200:
            data = response.json()
            cookie_data = data.get("cookie_data")
            if cookie_data and "weread.qq.com" in cookie_data:
                cookies = cookie_data["weread.qq.com"]
                cookie_str = "; ".join(
                    [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
                )
                result = cookie_str
        return result

    def get_cookie(self):
        url = os.getenv("CC_URL")
        if not url:
            url = "https://cookiecloud.malinkang.com/"
        id = os.getenv("CC_ID")
        password = os.getenv("CC_PASSWORD")
        cookie = os.getenv("WEREAD_COOKIE")
        if url and id and password:
            cookie = self.try_get_cloud_cookie(url, id, password)
        if not cookie or not cookie.strip():
            raise Exception("没有找到cookie，请按照文档填写cookie")
        return cookie

    def parse_cookie_string(self):
        cookies_dict = {}
        
        # 按分号分割 cookie
        cookie_pairs = self.cookie.split(';')
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key:  # 只添加非空的键
                    cookies_dict[key] = value
        
        # 直接使用 cookies_dict 创建 cookiejar
        cookiejar = cookiejar_from_dict(cookies_dict)
        
        return cookiejar

    def get_bookshelf(self):
        """获取书架列表"""
        # 先访问主页建立 session
        r = self.session.get(WEREAD_URL)
        # 如果响应中有 set-cookie，更新 cookies
        if 'set-cookie' in r.headers or 'Set-Cookie' in r.headers:
            set_cookie = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
            if set_cookie:
                # 解析并更新 cookie
                self._update_cookies_from_response(set_cookie)
        
        # 使用新的 API 端点替代 /shelf/sync
        # /api/user/notebook 直接返回数据（无需检查 errcode）
        r = self.session.get("https://weread.qq.com/api/user/notebook")
        # 再次检查响应头中的 set-cookie
        if 'set-cookie' in r.headers or 'Set-Cookie' in r.headers:
            set_cookie = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
            if set_cookie:
                self._update_cookies_from_response(set_cookie)
        
        if r.ok:
            data = r.json()
            # 新 API 直接返回书籍列表，不需要检查错误代码
            if "books" in data:
                # 返回完整响应，以保持向后兼容性
                # 新 API 不提供 bookProgress 和 archive，添加空值
                if "bookProgress" not in data:
                    data["bookProgress"] = []
                if "archive" not in data:
                    data["archive"] = []
                return data
            else:
                # 如果没有 books 字段，可能是错误响应
                self.handle_errcode(data)
                raise RuntimeError(f"Could not get bookshelf {r.text}")
        return {"books": [], "bookProgress": [], "archive": []}
    
    def refresh_cookies_from_homepage(self):
        """从主页响应刷新 Cookie - 基于 ObsidianWeRead 的方法"""
        try:
            r = self.session.get(WEREAD_URL)
            
            # 提取响应头中的 set-cookie
            set_cookie_header = (r.headers.get('set-cookie') or
                                 r.headers.get('Set-Cookie'))
            if set_cookie_header:
                self._update_cookies_from_response(set_cookie_header)
        except Exception:
            # 静默处理，不影响流程
            pass

    def _update_cookies_from_response(self, set_cookie_header):
        """从 set-cookie 响应头中提取并更新 cookies"""
        try:
            # set-cookie 头通常是这样的格式：
            # wr_skey=xxx; Path=/; Domain=.weread.qq.com; HttpOnly
            cookies = set_cookie_header.split(';')
            for cookie in cookies:
                cookie = cookie.strip()
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    key = key.strip()
                    if key.lower() not in ['path', 'domain', 'httponly',
                                          'secure', 'max-age', 'expires']:
                        # 这是一个真正的 cookie
                        self.session.cookies.set(key, value.strip())
        except Exception:
            # 静默处理，不影响流程
            pass
        
    def handle_errcode(self, data):
        """处理错误代码"""
        # 如果 data 是整数，直接使用
        if isinstance(data, int):
            errcode = data
        else:
            errcode = data.get("errcode", 0) if isinstance(data, dict) else 0
        
        if errcode == -2012 or errcode == -2010:
            print("::error::Cookie invalid or expired. ")

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_notebooklist(self):
        """获取笔记本列表"""
        # 使用 /api/user/notebook 端点（与 get_bookshelf 相同）
        # /user/notebooks 已被废弃或不可用，所以直接返回书架数据
        bookshelf = self.get_bookshelf()
        return bookshelf.get("books", [])

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_bookinfo(self, bookId):
        """获取书的详情
        从 /api/user/notebook 已有的数据中提取，不再调用 /web/book/info
        """
        # 尝试从书架数据中找到这本书
        bookshelf = self.get_bookshelf()
        for item in bookshelf.get("books", []):
            if item.get("bookId") == bookId and "book" in item:
                # 返回扁平化的书籍信息以保持兼容性
                return item.get("book", {})
        
        # 如果在书架中没找到，尝试调用 /web/book/info
        try:
            self.session.get(WEREAD_URL)
            params = dict(bookId=bookId)
            r = self.session.get(WEREAD_BOOK_INFO, params=params)
            
            # 更新 cookies
            if 'set-cookie' in r.headers or 'Set-Cookie' in r.headers:
                set_cookie = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
                if set_cookie:
                    self._update_cookies_from_response(set_cookie)
            
            if r.ok:
                data = r.json()
                # 检查是否有 info 字段（新 API 格式）
                if "info" in data and (data.get("errCode") == 0 or data.get("errCode") is None):
                    return data.get("info", {})
                # 尝试直接返回（可能是旧 API 格式）
                if data.get("errcode") == 0 or data.get("errcode") is None:
                    return data
                # 有错误
                self.handle_errcode(data)
        except Exception as e:
            pass
        
        # 最后回退：返回书籍基本信息（至少有 bookId）
        return {"bookId": bookId}


    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_bookmark_list(self, bookId):
        """获取书籍的划线列表
        需要先访问主页和笔记本API来建立完整的Session状态
        """
        try:
            # 步骤 1: 访问主页
            self.session.get(WEREAD_URL)
            
            # 步骤 2: 访问笔记本API来建立完整的Session状态
            # 这一步很重要，否则划线API会返回 -2012（登录超时）
            self.session.get("https://weread.qq.com/api/user/notebook")
            
            # 步骤 3: 获取划线列表
            params = dict(bookId=bookId)
            r = self.session.get(WEREAD_BOOKMARKLIST_URL, params=params)
            
            if r.ok:
                data = r.json()
                
                # 检查是否有错误
                if data.get("errCode") == -2012 or data.get("errCode") == -2010:
                    self.handle_errcode(data.get("errCode"))
                    return []
                
                # 返回划线列表
                bookmarks = data.get("updated", [])
                return bookmarks if bookmarks else []
            else:
                # HTTP 请求失败
                return []
        except Exception as e:
            print(f"⚠️  获取划线列表失败 (BookId: {bookId}): {e}")
            return []

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_read_info(self, bookId):
        """获取书籍阅读进度信息
        使用 /web/book/getProgress 端点获取阅读时间和进度
        """
        try:
            # 先访问主页激活 session
            self.session.get(WEREAD_URL)
            
            # 然后调用 /api/user/notebook 来建立完整的 session 状态
            # 这一步很重要，否则 /web/book/getProgress 会返回 -2012
            self.session.get("https://weread.qq.com/api/user/notebook")
            
            # 使用新的 getProgress 端点
            url = "https://weread.qq.com/web/book/getProgress"
            params = dict(bookId=bookId)
            r = self.session.get(url, params=params)
            
            # 更新 cookies
            if 'set-cookie' in r.headers or 'Set-Cookie' in r.headers:
                sc = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
                if sc:
                    self._update_cookies_from_response(sc)
            
            if r.ok:
                data = r.json()
                # 检查错误状态 (成功时 errCode 不存在或为 0)
                if (data.get("errCode") is None or data.get("errCode") == 0
                        or data.get("errcode") == 0):
                    # 提取 book 字段中的阅读进度
                    if "book" in data and data.get("book"):
                        book_info = data["book"]
                        return {
                            "bookId": bookId,
                            "markedStatus": 2,  # 默认在读
                            "readingProgress": book_info.get("progress", 0),
                            "readingTime": book_info.get("readingTime", 0),
                            "totalReadDay": 0,
                            "readDetail": {
                                "totalReadingTime":
                                book_info.get("readingTime", 0),
                                "beginReadingDate":
                                book_info.get("startReadingTime", 0),
                                "lastReadingDate":
                                book_info.get("updateTime", 0),
                            },
                            "bookInfo": {}
                        }
                    return data
        except Exception:
            pass
        
        # 回退：返回最小必要的结构
        return {
            "bookId": bookId,
            "markedStatus": 2,  # 默认为在读
            "readingProgress": 0,
            "readingTime": 0,
            "totalReadDay": 0,
            "readDetail": {},
            "bookInfo": {}
        }

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_review_list(self, bookId):
        """获取书籍的笔记/书评列表 - 基于 ObsidianWeRead"""
        try:
            # 刷新 Cookie
            self.refresh_cookies_from_homepage()
            
            # 获取笔记列表 - synckey 参数必须小写
            params = dict(bookId=bookId, listType=11, mine=1, synckey=0)
            r = self.session.get(WEREAD_REVIEW_LIST_URL, params=params)
            
            if r.ok:
                data = r.json()
                
                # 处理 -2012 错误
                if data.get("errCode") == -2012:
                    print("Got -2012 error, will retry...")
                    return []
                
                # 处理笔记列表
                reviews = data.get("reviews")
                if not reviews:
                    return []
                
                # 提取实际的笔记内容
                reviews = [x.get("review") for x in reviews
                           if x.get("review")]
                
                # 为点评类型添加 chapterUid
                reviews = [
                    {"chapterUid": 1000000, **x}
                    if x.get("type") == 4 else x
                    for x in reviews
                ]
                return reviews
            else:
                # HTTP 请求失败
                return []
        except Exception as e:
            print("获取笔记列表失败 (BookId: {}): {}".format(bookId, e))
            return []



    
    def get_api_data(self):
        self.session.get(WEREAD_URL)
        r = self.session.get(WEREAD_HISTORY_URL)
        if r.ok:
            return r.json()
        else:
            errcode = r.json().get("errcode",0)
            self.handle_errcode(errcode)
            raise Exception(f"get history data failed {r.text}")

    

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_chapter_info(self, bookId):
        """获取书籍的章节信息
        需要先访问主页和笔记本API来建立完整的Session状态
        """
        try:
            # 步骤 1: 访问主页
            self.session.get(WEREAD_URL)
            
            # 步骤 2: 访问笔记本API来建立完整的Session状态
            # 这一步很重要，否则章节API会返回 -2012（登录超时）
            self.session.get("https://weread.qq.com/api/user/notebook")
            
            # 步骤 3: 获取章节信息
            body = {"bookIds": [bookId], "synckeys": [0], "teenmode": 0}
            r = self.session.post(WEREAD_CHAPTER_INFO, json=body)
            
            if r.ok:
                data = r.json()
                
                # 检查是否有错误
                if data.get("errCode") == -2012 or data.get("errCode") == -2010:
                    self.handle_errcode(data.get("errCode"))
                    return {}
                
                # 检查数据结构
                if (
                    "data" in data
                    and len(data["data"]) >= 1
                    and "updated" in data["data"][0]
                ):
                    update = data["data"][0]["updated"]
                    
                    # 添加点评章节
                    update.append(
                        {
                            "chapterUid": 1000000,
                            "chapterIdx": 1000000,
                            "updateTime": 1683825006,
                            "readAhead": 0,
                            "title": "点评",
                            "level": 1,
                        }
                    )
                    
                    return {item["chapterUid"]: item for item in update}
                
                return {}
            else:
                # HTTP 请求失败
                return {}
        except Exception as e:
            print(f"⚠️  获取章节信息失败 (BookId: {bookId}): {e}")
            return {}

    def transform_id(self, book_id):
        id_length = len(book_id)
        if re.match("^\\d*$", book_id):
            ary = []
            for i in range(0, id_length, 9):
                ary.append(format(int(book_id[i : min(i + 9, id_length)]), "x"))
            return "3", ary

        result = ""
        for i in range(id_length):
            result += format(ord(book_id[i]), "x")
        return "4", [result]

    def calculate_book_str_id(self, book_id):
        md5 = hashlib.md5()
        md5.update(book_id.encode("utf-8"))
        digest = md5.hexdigest()
        result = digest[0:3]
        code, transformed_ids = self.transform_id(book_id)
        result += code + "2" + digest[-2:]

        for i in range(len(transformed_ids)):
            hex_length_str = format(len(transformed_ids[i]), "x")
            if len(hex_length_str) == 1:
                hex_length_str = "0" + hex_length_str

            result += hex_length_str + transformed_ids[i]

            if i < len(transformed_ids) - 1:
                result += "g"

        if len(result) < 20:
            result += digest[0 : 20 - len(result)]

        md5 = hashlib.md5()
        md5.update(result.encode("utf-8"))
        result += md5.hexdigest()[0:3]
        return result

    def get_url(self, book_id):
        return f"https://weread.qq.com/web/reader/{self.calculate_book_str_id(book_id)}"
