# 划线和笔记获取问题诊断报告

## 问题概述

运行诊断工具后发现，划线（Bookmark）和笔记（Review）无法正常获取。主要错误是：
```
errCode: -2012
errMsg: "登录超时"
```

## 诊断结果

### ✅ 正常的部分
- **笔记本列表**: ✅ 成功获取 36 本笔记本
- **书架列表**: ✅ 正常工作

### ❌ 失败的部分
1. **划线列表** (get_bookmark_list)
   - 状态: 为空
   - 原因: API 返回 -2012 错误

2. **书评/笔记** (get_review_list)
   - 状态: 为空
   - 原因: API 返回 -2012 错误

3. **章节信息** (get_chapter_info)
   - 状态: 为空
   - 错误: `{"errCode":-2012,"errMsg":"登录超时"}`
   - 原因: API 返回 -2012 错误

## 根本原因分析

### 错误代码 -2012 含义
- **-2012**: 登录超时 (Login timeout)
- **-2010**: 会话过期 (Session expired)

这些错误表示 WeChat Reading 服务器拒绝了请求，因为认证信息无效或过期。

### 为什么书架信息仍然可以获取？
书架信息通过 `/api/user/notebook` 端点获取，这个端点可能有不同的认证机制或缓存策略，而划线、笔记、章节等接口需要更严格的认证。

## 为什么会出现 -2012 错误？

### 可能原因

1. **Cookie 已过期**（最可能）
   - WeChat Reading 的 Cookie 有时间限制
   - 自上次设置后已经超过有效期
   - 需要重新从微信读书更新 Cookie

2. **Cookie 格式或内容错误**
   - Cookie 字符串解析有问题
   - 关键的认证字段缺失或损坏

3. **Session 状态问题**
   - 某些请求的顺序或流程不对
   - 缺少必要的"预热"请求

4. **网络问题**
   - 微信读书服务器端拒绝连接
   - VPN 或代理导致 IP 被限制

## 解决方案

### 方案 1: 更新 Cookie（推荐首先尝试）

1. **获取新的 Cookie**
   - 方式 A：使用 CookieCloud 同步（如已配置）
   - 方式 B：手动从浏览器提取 Cookie
   - 方式 C：使用官方的 Cookie 获取工具

2. **更新环境变量**
   ```bash
   # 方式 1: 编辑 .env 文件
   WEREAD_COOKIE="新的 cookie 字符串"
   
   # 方式 2: 通过 CookieCloud 自动更新
   CC_URL="https://cookiecloud...."
   CC_ID="your_id"
   CC_PASSWORD="your_password"
   ```

3. **测试新 Cookie**
   ```bash
   python tests/diagnose_bookmark_review.py
   ```

### 方案 2: 检查 Cookie 格式

运行以下命令检查 Cookie 是否正确解析：

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
cookie = os.getenv('WEREAD_COOKIE', '')
print(f'Cookie 长度: {len(cookie)}')
print(f'Cookie 前 100 字符: {cookie[:100]}')
print(f'Cookie 是否包含分号: {\";\", in cookie}')
"
```

### 方案 3: 改进 API 错误处理

在 `weread_api.py` 中添加更详细的日志记录：

```python
def handle_errcode(self, data):
    """处理错误代码"""
    if isinstance(data, int):
        errcode = data
    else:
        errcode = data.get("errcode", 0) if isinstance(data, dict) else 0
    
    if errcode == -2012 or errcode == -2010:
        error_msg = "微信读书Cookie过期了，请参考文档重新设置。"
        print(f"❌ {error_msg}")
        print(f"   错误代码: {errcode}")
        print(f"   错误详情: {data}")
        # TODO: 可以在这里添加自动重试或告警机制
```

### 方案 4: 添加重试逻辑

某些 API 需要"预热"（先访问主页建立 Session），可能需要改进：

```python
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def get_bookmark_list(self, bookId):
    # 确保 Session 已建立
    self.session.get(WEREAD_URL)
    
    # 可能需要添加额外的预热请求
    self.session.get("https://weread.qq.com/api/user/notebook")
    
    params = dict(bookId=bookId)
    r = self.session.get(WEREAD_BOOKMARKLIST_URL, params=params)
    # ... 后续代码
```

## 环境检查清单

- [ ] WEREAD_COOKIE 变量已设置
- [ ] Cookie 包含微信读书的认证信息
- [ ] Cookie 最近 24 小时内更新过
- [ ] 网络连接正常
- [ ] 不存在 VPN 或代理限制

## 进一步诊断步骤

如果上述方案都不行，运行以下命令获取更多信息：

```bash
# 1. 检查原始 API 响应
python -c "
from weread2notionpro.weread_api import WeReadApi
api = WeReadApi()
import json
resp = api.session.get('https://weread.qq.com/web/book/bookmarklist', 
                        params={'bookId': '3300129525'})
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
"

# 2. 检查 Cookie 内容
python -c "
from weread2notionpro.weread_api import WeReadApi
api = WeReadApi()
print('Cookies:')
for cookie in api.session.cookies:
    print(f'  {cookie.name}={cookie.value[:50]}...')
"
```

## 相关链接

- [Cookie 获取文档](https://mp.weixin.qq.com/s/B_mqLUZv7M1rmXRsMlBf7A)
- [WeRead API 错误代码文档](https://weread.qq.com/docs)
- [诊断脚本](tests/diagnose_bookmark_review.py)

## 状态

🔴 **待解决** - Cookie 验证问题
- 需要更新 WEREAD_COOKIE
- 或需要调查 API 认证机制

## 下一步

1. 获取新的 Cookie 并更新 .env 文件
2. 运行诊断脚本验证
3. 检查 GitHub Actions 是否能正常同步
