# WeRead API 文档

> 基于 2025-10-24 的探测和测试结果

## 工作的端点 (Working)

### 1. 获取笔记本和书架 ✅
**端点**: `GET https://weread.qq.com/api/user/notebook`

**请求头**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
Accept: application/json, text/plain, */*
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Accept-Encoding: gzip, deflate, br
Content-Type: application/json
Referer: https://weread.qq.com/
```

**参数**: 无

**响应示例**:
```json
{
  "synckey": 1761282941,
  "totalBookCount": 36,
  "noBookReviewCount": 0,
  "books": [
    {
      "bookId": "3300129525",
      "book": {
        "bookId": "3300129525",
        "title": "书名",
        "author": "作者",
        "cover": "封面 URL",
        // ... 其他书籍信息
      },
      "noteCount": 2,           // 笔记数
      "bookmarkCount": 0,        // 划线数
      "reviewCount": 0,          // 书评数
      "reviewLikeCount": 0,
      "reviewCommentCount": 0,
      "sort": 1761240419
    }
  ]
}
```

**用途**: 
- 获取用户的所有书籍列表
- 包含每本书的基本信息和笔记/划线/评论数量统计
- 是最关键的端点，几乎所有其他操作都基于此

---

### 2. 获取书籍划线 ✅
**端点**: `GET https://weread.qq.com/web/book/bookmarklist`

**参数**:
- `bookId` (必需): 书籍 ID

**请求头**:
- 必须包含 `Referer: https://weread.qq.com/`
- 必须在 session 中调用过 `/api/user/notebook`

**响应示例**:
```json
{
  "updated": [
    {
      "bookmarkId": "xyz",
      "bookId": "3300129525",
      "blockId": "block123",
      "markText": "划线的文本",
      "markTextRange": "0-100",
      "range": "0-100",
      "colorStyle": 1,
      "style": 0,
      "createTime": 1609459200000,
      "chapterUid": 1,
      "bookVersion": 1
    }
  ]
}
```

**注意**:
- 只有调用过 `/api/user/notebook` 后才能调用此端点
- 必须使用 Referer 请求头

---

## 有问题的端点 (Problematic - 返回 -2012)

### 获取书籍信息
**端点**: `GET https://weread.qq.com/web/book/info?bookId={bookId}`
- **问题**: 返回 errCode: -2012 (登录超时)
- **备选方案**: 从 `/api/user/notebook` 的返回中获取书籍信息

### 获取阅读进度
**端点**: `GET https://weread.qq.com/web/book/getProgress?bookId={bookId}`
- **问题**: 返回 errCode: -2012 (登录超时)
- **备选方案**: 无

### 获取笔记列表
**端点**: `GET https://weread.qq.com/web/review/list?bookId={bookId}&listType=11&mine=1&syncKey=0`
- **问题**: 返回 errCode: -2012 (登录超时)
- **备选方案**: 无（noteCount 统计信息可从 `/api/user/notebook` 获取）

### 获取章节信息
**端点**: `POST https://weread.qq.com/web/book/chapterInfos`
```json
{
  "bookIds": ["3300129525"],
  "synckeys": [0],
  "teenmode": 0
}
```
- **问题**: 返回 errCode: -2012 (登录超时)
- **备选方案**: 无

---

## 不存在的端点 (404 Not Found)

- `GET https://weread.qq.com/web/readdata/summary?synckey=0`
- `GET https://weread.qq.com/web/readdata/detail?synckey=0`
- `GET https://weread.qq.com/api/readinfo?bookId={bookId}`
- `GET https://weread.qq.com/api/bookmark?bookId={bookId}`
- `GET https://weread.qq.com/api/review?bookId={bookId}`

---

## 认证问题分析

### 错误代码
- `-2012`: 登录超时 (Login Timeout)
- `-2010`: 其他认证错误

### 原因推测
1. WeChat Reading 可能改变了认证机制
2. 某些端点可能已被废弃
3. 某些端点可能需要特殊的 Token 或授权
4. 可能存在 IP 限制或频率限制

### 解决方案
1. **划线功能**: ✅ 已通过添加 Referer 解决
2. **笔记功能**: ❌ 无法直接调用 API，可能需要：
   - 寻找替代端点
   - 使用 Web Scraping
   - 考虑使用第三方服务（如 NotionHub）

---

## 建议改进方向

### 短期
1. 利用 `/api/user/notebook` 的 `noteCount` 和 `bookmarkCount` 字段
2. 对于有划线的书籍，调用 bookmarklist 获取详细数据
3. 对于笔记，显示数量但无法获取详细内容

### 中期
1. 实现 Web Scraping 来获取笔记数据
2. 尝试从浏览器 DevTools 抓取真实请求
3. 研究 NotionHub 的实现方式

### 长期
1. 联系 WeChat Reading 官方获取 API 授权
2. 考虑实现浏览器扩展方案
3. 寻找社区中的其他解决方案

---

## 测试环境
- 时间: 2025-10-24
- Cookie: 有效
- 用户: 已认证
- 测试结果: 见 `tests/api_discovery.py`
