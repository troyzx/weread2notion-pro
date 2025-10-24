# WeRead API 现状总结 (2025-10-24)

## 核心发现

通过详细的 API 探测，我们发现了 WeRead API 的真实可用情况：

### ✅ 完全可用
- `/api/user/notebook` - 获取笔记本和书架列表
- `/web/book/bookmarklist` - 获取书籍划线（需要 Referer 请求头）

### ❌ 无法使用 (-2012 Login Timeout 错误)
- `/web/book/info` - 获取书籍详细信息
- `/web/book/getProgress` - 获取阅读进度
- `/web/review/list` - 获取笔记列表
- `/web/book/chapterInfos` - 获取章节信息
- `/web/shelf/sync` - 获取书架同步数据

### 🚫 已废弃 (404 Not Found)
- 所有 `/api/readinfo`, `/api/bookmark`, `/api/review` 变体
- `/web/readdata/*` 端点

---

## 当前代码状态

### 已修复
✅ **划线功能恢复** (2025-10-24)
- 添加了 `Referer: https://weread.qq.com/` 请求头
- 修改了 `get_bookmark_list()` 方法
- 现在能获取有划线的书籍的划线列表

### 仍有问题
❌ **笔记功能无法工作**
- `review/list` 端点持续返回 -2012 错误
- 无论如何调整请求头都无法解决
- 可能需要特殊的认证令牌或已被废弃

---

## 解决方案建议

### 选项 A: 接受当前限制（快速）
```python
# 优势:
✓ 划线功能已恢复
✓ 可以显示笔记数量（从 noteCount 字段）
✓ 无需外部依赖

# 缺点:
✗ 无法获取具体的笔记内容
✗ 阅读进度等信息丢失
```

### 选项 B: Web Scraping（中等难度）
```python
# 通过浏览器自动化获取数据
# 工具: Selenium, Playwright, Puppeteer

# 优势:
✓ 可以获取所有数据
✓ 不依赖 API

# 缺点:
✗ 速度慢
✗ 易受网站更新影响
✗ 资源消耗大
```

### 选项 C: 使用 NotionHub（推荐）
```python
# NotionHub 是一个商业产品，已解决所有这些问题
# https://www.notionhub.app/

# 优势:
✓ 功能完整
✓ 维护活跃
✓ 可靠性高

# 缺点:
✗ 需要付费或授权
✗ 失去代码控制权
```

---

## 建议行动计划

### 第一步（立即）
1. ✅ 保存目前的修复（Referer 请求头）
2. ✅ 为划线功能添加测试
3. ✅ 创建 API 文档

### 第二步（本周）
1. 调查是否存在替代的笔记获取方式
2. 尝试从浏览器的网络请求中学习
3. 研究 NotionHub 的实现方式

### 第三步（本月）
1. 如果需要笔记功能，评估 Web Scraping 或 NotionHub
2. 或者干脆接受只有划线的限制，更新文档和 UI
3. 发布新版本说明已知限制

---

## 技术细节

### Referer 请求头的作用
我们发现 `Referer: https://weread.qq.com/` 请求头对 bookmarklist 端点至关重要：

**不带 Referer**:
```
GET /web/book/bookmarklist?bookId=XXX
→ 返回: {"errCode": -2012, "errMsg": "登录超时"}
```

**带 Referer**:
```
GET /web/book/bookmarklist?bookId=XXX
Referer: https://weread.qq.com/
→ 返回: {"updated": [...]} ✅
```

但其他端点（review/list, getProgress 等）无论如何都无法正常工作。

### 可能的原因
1. **认证机制变化**: WeRead 可能实现了新的认证方式
2. **端点版本化**: 不同的端点可能需要不同的认证等级
3. **故意限制**: WeRead 可能故意限制第三方工具的访问
4. **API 迁移**: 旧端点已迁移到新位置但未文档化

---

## 后续工作

### 如果要继续探索
```bash
# 1. 使用浏览器 DevTools 抓取真实请求
# 2. 对比成功和失败的请求差异
# 3. 尝试从浏览器 Console 提取 Token 或 Session 信息

# 抓取工具建议:
- mitmproxy (中间人代理)
- Charles Proxy
- Fiddler
- Browser DevTools Network Tab
```

### 社区资源
- 搜索 "weread api python" 在 GitHub
- 查看 obsidian-weread 插件的实现
- 监控 WeRead 官方公告

---

## 结论

目前的情况：
- **划线**功能：✅ 已恢复
- **笔记**功能：❌ 无法通过 API 获取
- **其他**功能：❌ 大多数已废弃或被限制

**建议**: 
1. 发布当前版本，说明支持划线但不支持笔记
2. 继续投资或迁移到 NotionHub
3. 或者等待社区找到新的解决方案

---

**最后更新**: 2025-10-24
**测试环境**: macOS, Python 3.13.9
**API 版本**: WeRead Web API (未官方发布)
