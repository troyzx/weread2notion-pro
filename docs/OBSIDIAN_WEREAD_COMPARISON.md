# ObsidianWeRead 插件 vs 当前项目 - API 实现对比

## 关键发现

### 1. Cookie 刷新机制 ✅

**ObsidianWeRead 的做法**:
```typescript
async refreshCookie() {
    const req = {
        url: this.baseUrl,
        method: 'HEAD',  // 使用 HEAD 请求刷新
        headers: this.getHeaders()
    };
    const resp = await requestUrl(req);
    const respCookie = resp.headers['set-cookie'] || resp.headers['Set-Cookie'];
    
    if (respCookie !== undefined && this.checkCookies(respCookie)) {
        // 更新 cookies
        this.updateCookies(respCookie);
    }
}
```

**关键点**:
- 首先访问主页时自动刷新 Cookie
- 捕获响应头中的 `set-cookie`
- 提取新的 `wr_skey` 等关键 Cookie
- 在后续请求中使用更新的 Cookie

### 2. -2012 错误处理 ✅

**ObsidianWeRead 的做法**:
```typescript
if (resp.json.errcode == -2012) {
    // 登录超时 -2012
    console.log('weread cookie expire retry refresh cookie...');
    await this.refreshCookie();
    // 重试请求
}
```

**含义**:
- `-2012` 是"登录超时"，不一定是 Cookie 过期
- 解决方案是刷新 Cookie（从响应头获取新的 set-cookie）
- 然后重试请求

### 3. 所有端点都在使用 ✅

他们成功使用的端点：
- ✅ `GET /api/user/notebook` - 获取笔记本
- ✅ `GET /web/book/info?bookId={bookId}` - 获取书籍信息
- ✅ `GET /web/book/bookmarklist?bookId={bookId}` - 获取划线
- ✅ `GET /web/review/list?bookId={bookId}&listType=11&mine=1&synckey=0` - 获取笔记
- ✅ `POST /web/book/chapterInfos` - 获取章节
- ✅ `GET /web/book/getProgress?bookId={bookId}` - 获取阅读进度

**问题**：我们为什么得不到这些？

## 解决方案

根据 ObsidianWeRead 的实现，我们需要：

### 1. 实现 Cookie 自动刷新

```python
async def refresh_cookie(self):
    """从响应头刷新 Cookie"""
    r = self.session.get(WEREAD_URL, allow_redirects=True)
    
    # 提取 set-cookie 响应头
    set_cookie = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
    if set_cookie:
        self._update_cookies_from_response(set_cookie)
```

### 2. 改进错误处理

```python
def get_review_list(self, bookId):
    """获取笔记列表，带重试"""
    try:
        r = self.session.get(WEREAD_REVIEW_LIST_URL, params=params)
        data = r.json()
        
        if data.get("errCode") == -2012:
            # 刷新 Cookie 并重试
            self.refresh_cookie()
            r = self.session.get(WEREAD_REVIEW_LIST_URL, params=params)
            data = r.json()
        
        return data.get("reviews", [])
    except Exception as e:
        print(f"Error: {e}")
        return []
```

### 3. 检查请求头

对比 ObsidianWeRead：
```typescript
private getHeaders() {
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Content-Type': 'application/json',
        Cookie: getCookieString(get(settingsStore).cookies)
    };
}
```

**注意**:
- 没有设置 `Referer` 请求头！
- 使用 `accept` (小写) 而不是 `Accept`
- 包含 Cookie 在请求头中

## 可能的原因分析

为什么我们的请求失败而 ObsidianWeRead 的成功？

1. **Cookie 状态**：可能需要定期刷新而不是一次性设置
2. **会话维护**：需要持续访问主页来维护 Cookie 的有效性
3. **User-Agent**：他们使用的是 Chrome 73 而不是我们的较新版本
4. **响应头处理**：正确处理 `set-cookie` 响应头很关键

## 建议改进步骤

1. **立即修改** `_get_headers()`:
   - 移除 `Referer` 请求头
   - 尝试使用他们的 User-Agent

2. **添加 Cookie 刷新机制**:
   - 定期调用主页来更新 Cookie
   - 捕获响应头中的新 Cookie
   - 在每个请求前检查是否需要刷新

3. **改进重试逻辑**:
   - 当收到 -2012 时，先刷新 Cookie
   - 然后自动重试该请求

4. **增加调试信息**:
   - 记录所有请求和响应
   - 输出 Cookie 状态
   - 对比成功和失败的请求

## 代码修改建议

```python
def _get_headers(self):
    """获取标准的浏览器请求头 - 参考 ObsidianWeRead"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.103 Safari/537.36',  # 改用他们的版本
        'accept': 'application/json, text/plain, */*',  # 小写
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        # 移除 Referer
    }

def refresh_cookies_from_homepage(self):
    """从主页响应刷新 Cookie"""
    r = self.session.get(WEREAD_URL)
    
    set_cookie_header = r.headers.get('set-cookie') or r.headers.get('Set-Cookie')
    if set_cookie_header:
        self._update_cookies_from_response(set_cookie_header)
        print("✓ Cookies refreshed from homepage")

def get_review_list_with_retry(self, bookId, max_retries=2):
    """带重试的获取笔记列表"""
    for attempt in range(max_retries):
        try:
            # 先刷新 Cookie
            self.refresh_cookies_from_homepage()
            
            params = dict(bookId=bookId, listType=11, mine=1, syncKey=0)
            r = self.session.get(WEREAD_REVIEW_LIST_URL, params=params)
            data = r.json()
            
            if data.get("errCode") == -2012:
                if attempt < max_retries - 1:
                    print(f"Got -2012, refreshing cookies and retrying...")
                    continue
            
            reviews = data.get("reviews", [])
            return [x.get("review") for x in reviews if x.get("review")]
        
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
    
    return []
```

## 总结

ObsidianWeRead 的成功秘诀：
1. ✅ 定期从主页刷新 Cookie
2. ✅ 捕获和应用响应头的新 Cookie
3. ✅ 对 -2012 错误进行重试
4. ✅ 使用一致的请求头

**建议**: 采纳他们的方法，特别是 Cookie 刷新机制。
