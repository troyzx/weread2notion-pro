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
        """
        获取阅读历史数据
        优先使用新的readdata/detail API，如果失败则回退到传统方法
        """
        print("🔍 获取阅读统计数据...")
        
        try:
            # 优先使用新的详细API
            return self.get_readtiming_detail_data()
        except Exception as e:
            print(f"⚠️  新API失败，使用传统方法: {e}")
            return self._get_api_data_legacy()

    @retry(stop_max_attempt_number=3, wait_fixed=5000)
    def get_readtiming_detail_data(self):
        """
        从微信读书API获取详细阅读数据 - 使用新的readdata/detail API
        返回完整的阅读统计信息，包括年度报告、阅读时间等
        
        返回数据结构分析:
        - readTimes: dict - 日期时间戳 -> 阅读分钟数
        - readDays: int - 总阅读天数
        - totalReadTime: int - 总阅读时间(分钟)
        - yearReport: list - 年度报告数据，每个年度包含每月阅读时间
        - preferBooks: list - 偏好书籍列表
        - preferCategory: list - 偏好分类统计
        - preferAuthor: list - 偏好作者统计
        - medals: list - 勋章成就
        - readStat: list - 阅读统计概览
        - shareInfo: dict - 分享信息
        """
        try:
            # 优先尝试从环境变量获取移动端认证信息
            vid = os.getenv("WEREAD_VID")
            skey = os.getenv("WEREAD_SKEY")
            
            if not vid or not skey:
                # 如果环境变量不存在，尝试从session cookies中提取（网页端）
                vid = self.session.cookies.get("wr_vid", "")
                skey = self.session.cookies.get("wr_skey", "")
                
                if vid and skey:
                    print("📱 使用网页端cookie进行认证")
                else:
                    print("⚠️  未找到移动端认证信息(vid/skey)，请设置环境变量WEREAD_VID和WEREAD_SKEY")
                    print("   或者使用传统方法获取数据")
                    return self._get_api_data_legacy()
            
            print("🔍 使用新的readdata/detail API获取阅读统计数据...")
            
            # 使用新的API端点
            url = "https://i.weread.qq.com/readdata/detail?baseTime=0&defaultPreferBook=0&mode=overall"
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'channelId': 'AppStore',
                'vid': vid,
                'Host': 'i.weread.qq.com',
                'basever': '8.2.0.34',
                'skey': skey,
                'v': '8.2.0.34',
                'Accept-Language': 'zh-Hans-CN;q=1',
                'User-Agent': 'WeRead/8.2.0 (iPad; iOS 26.0; Scale/2.00)',
                'Content-Type': 'application/json',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否有错误
                if data.get("errCode") and data["errCode"] != 0:
                    print(f"⚠️  API返回错误: {data}")
                    return self._get_api_data_legacy()
                
                print("✅ 成功获取详细阅读数据")
                self._analyze_readtiming_data(data)
                
                # 转换为与原来API兼容的格式
                return self._convert_to_readtimes_format(data)
            else:
                print(f"⚠️  API请求失败 (状态码: {response.status_code})，使用传统方法")
                return self._get_api_data_legacy()
                
        except Exception as e:
            print(f"⚠️  获取详细阅读数据失败: {e}，使用传统方法")
            return self._get_api_data_legacy()

    def _analyze_readtiming_data(self, data):
        """
        详细分析readdata/detail API返回的数据结构
        """
        print("\n📊 详细阅读数据分析:")
        
        # 基本统计信息
        if "readTimes" in data:
            read_times = data["readTimes"]
            print(f"  📅 阅读时间点数: {len(read_times)}")
            if read_times:
                total_minutes = sum(read_times.values())
                print(f"  ⏰ 总阅读时间: {total_minutes} 分钟")
                print(f"  📊 覆盖天数: {len(read_times)} 天")
        
        if "readDays" in data:
            print(f"  📆 累计阅读天数: {data['readDays']} 天")
        
        if "totalReadTime" in data:
            print(f"  🕐 总阅读时长: {data['totalReadTime']} 分钟")
        
        # 阅读统计概览
        if "readStat" in data and data["readStat"]:
            print("  📈 阅读统计概览:")
            for stat in data["readStat"]:
                print(f"    • {stat.get('stat', '')}: {stat.get('counts', '')}")
        
        # 年度报告
        if "yearReport" in data and data["yearReport"]:
            print(f"  📊 年度报告: {len(data['yearReport'])} 个年度")
            for year_data in data["yearReport"]:
                year = year_data.get("title", "")
                times = year_data.get("times", [])
                if times:
                    year_total = sum(times)
                    print(f"    • {year}: {year_total} 分钟 ({len([t for t in times if t > 0])}个月有阅读)")
        
        # 偏好信息
        if "preferBooks" in data:
            print(f"  📚 偏好书籍数量: {len(data['preferBooks'])}")
        
        if "preferCategory" in data and data["preferCategory"]:
            print(f"  🏷️  偏好分类数量: {len(data['preferCategory'])}")
        
        if "preferAuthor" in data and data["preferAuthor"]:
            print(f"  ✍️  偏好作者数量: {len(data['preferAuthor'])}")
        
        # 勋章成就
        if "medals" in data and data["medals"]:
            print(f"  🏆 勋章成就数量: {len(data['medals'])}")
        
        # 分享信息
        if "shareInfo" in data and data["shareInfo"]:
            share_info = data["shareInfo"]
            print("  📤 分享信息:")
            if "title" in share_info:
                print(f"    • 标题: {share_info['title']}")
            if "totalReadingDay" in share_info:
                print(f"    • 总阅读天数: {share_info['totalReadingDay']}")
            if "hadReadingCount" in share_info:
                print(f"    • 已读书籍: {share_info['hadReadingCount']}")
            if "finishReadingCount" in share_info:
                print(f"    • 读完书籍: {share_info['finishReadingCount']}")
            if "notesCount" in share_info:
                print(f"    • 笔记数量: {share_info['notesCount']}")

    def _convert_to_readtimes_format(self, data):
        """
        将readdata/detail API的数据转换为与原来API兼容的readTimes格式
        
        转换逻辑:
        1. 如果有readTimes字段，直接使用（已经是时间戳->分钟的格式）
        2. 如果有yearReport数据，展开为每月的时间戳
        3. 合并所有数据点
        """
        result_read_times = {}
        
        # 1. 直接使用readTimes数据（如果存在）
        if "readTimes" in data and data["readTimes"]:
            result_read_times.update(data["readTimes"])
        
        # 2. 从年度报告中提取每月数据
        if "yearReport" in data and data["yearReport"]:
            import time
            import calendar
            
            for year_data in data["yearReport"]:
                year = int(year_data.get("title", "0"))
                times = year_data.get("times", [])
                
                # times是12个月的数据，从1月到12月
                for month_idx, minutes in enumerate(times):
                    if minutes > 0:  # 只处理有阅读时间的月份
                        month = month_idx + 1  # 月份从1开始
                        
                        # 计算该月第一天的时间戳
                        first_day = time.struct_time((year, month, 1, 0, 0, 0, -1, -1, -1))
                        month_timestamp = int(time.mktime(first_day))
                        
                        # 如果该月没有readTimes数据，则添加
                        if month_timestamp not in result_read_times:
                            result_read_times[month_timestamp] = minutes
        
        # 3. 按时间戳排序
        sorted_read_times = dict(sorted(result_read_times.items()))
        
        print(f"📊 转换完成: {len(sorted_read_times)} 个阅读数据点")
        
        return {"readTimes": sorted_read_times}

    def _get_api_data_legacy(self):
        """
        获取阅读历史数据 - 传统方法（从单本书籍进度数据聚合）
        作为新API的回退方案
        """
        print("🔄 使用传统方法获取阅读统计数据...")
        
        # 建立完整的 session 状态
        self.session.get(WEREAD_URL)
        self.session.get("https://weread.qq.com/api/user/notebook")
        
        # 获取所有书籍
        bookshelf = self.get_bookshelf()
        books = bookshelf.get("books", [])
        
        if not books:
            print("⚠️  未找到任何书籍，返回空数据")
            return {"readTimes": {}}
        
        print(f"📚 发现 {len(books)} 本书，开始收集阅读数据...")
        
        read_times = {}
        total_books_processed = 0
        
        for book_item in books:
            book_id = book_item.get("bookId")
            if not book_id:
                continue
                
            try:
                # 获取书籍的阅读信息
                read_info = self.get_read_info(book_id)
                
                if read_info and read_info.get("readingTime", 0) > 0:
                    # 提取阅读时间和日期信息
                    reading_time = read_info.get("readingTime", 0)
                    last_reading_date = read_info.get("readDetail", {}).get("lastReadingDate", 0)
                    
                    if last_reading_date > 0:
                        # 将最后阅读日期转换为当天的开始时间戳 (Unix 时间戳)
                        import time
                        # last_reading_date 是秒级时间戳，我们需要将其转换为当天的 00:00:00
                        date_struct = time.localtime(last_reading_date)
                        day_start_timestamp = int(time.mktime(time.struct_time((
                            date_struct.tm_year, date_struct.tm_mon, date_struct.tm_mday,
                            0, 0, 0,  # 00:00:00
                            date_struct.tm_wday, date_struct.tm_yday, date_struct.tm_isdst
                        ))))
                        
                        # 累加同一天的阅读时间
                        if day_start_timestamp not in read_times:
                            read_times[day_start_timestamp] = 0
                        read_times[day_start_timestamp] += reading_time
                        
                        total_books_processed += 1
                        print(f"  ✅ {book_item.get('book', {}).get('title', '未知书籍')[:20]}...: {reading_time}秒")
                
            except Exception as e:
                print(f"  ⚠️  处理书籍 {book_id} 时出错: {e}")
                continue
        
        print(f"📊 成功处理 {total_books_processed} 本书，收集到 {len(read_times)} 天的阅读数据")
        
        # 转换为原来 API 的格式 (时间戳 -> 分钟)
        formatted_read_times = {}
        for date_ts, seconds in read_times.items():
            # 将秒转换为分钟 (原来 API 返回分钟)
            minutes = seconds // 60
            if minutes > 0:  # 只保留有意义的阅读时间
                formatted_read_times[int(date_ts)] = minutes
        
        result = {"readTimes": formatted_read_times}
        print(f"📈 总阅读时间: {sum(formatted_read_times.values())} 分钟，跨越 {len(formatted_read_times)} 天")
        
        return result

    

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
