# Notion API 多数据源 (Multi-Database) 修复说明

## 问题描述

在使用 Notion API 2025-09-03 版本时，查询包含多个数据源的数据库会返回以下错误：

```json
{
  "code": "validation_error",
  "message": "Multiple data sources found for database query",
  "additional_data": {
    "error_type": "multiple_data_sources_for_database"
  }
}
```

这是因为 Notion API 在新版本中改变了查询多源数据库的方式。

## API 版本变化

### 旧版本 (≤ 2024-06-28)
**Endpoint:** `PATCH /v1/databases/:database_id/query`

适用于单数据源或简单数据库。

### 新版本 (≥ 2025-09-03)
**Endpoint:** `PATCH /v1/data_sources/:data_source_id/query`

需要以下步骤：
1. 调用 `GET /v1/databases/:database_id` 获取 `data_sources` 列表
2. 使用返回的 `data_source_id` 调用新的 query endpoint

## 修复内容

### 修改的方法：`query_all()` in `notion_helper.py`

**主要变化：**

1. **获取数据库元数据** 
   - 使用 `GET /v1/databases/{database_id}` 获取数据库信息
   - 提取 `data_sources[0]["id"]` 作为 `data_source_id`

2. **使用新的查询 endpoint**
   - 旧：`POST /v1/databases/{database_id}/query`
   - 新：`POST /v1/data_sources/{data_source_id}/query`

3. **API 版本**
   - 更新 `Notion-Version` header 为 `2025-09-03`

### 代码示例

**修改前：**
```python
def query_all(self, database_id):
    """获取database中所有的数据"""
    results = []
    has_more = True
    start_cursor = None
    while has_more:
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = self.client.client.post(url, json=body, headers=headers)
        # 处理响应...
    return results
```

**修改后：**
```python
def query_all(self, database_id):
    """获取database中所有的数据"""
    results = []
    
    # 步骤 1: 获取 data_source_id
    db_url = f"https://api.notion.com/v1/databases/{database_id}"
    db_response = self.client.client.get(db_url, headers=headers)
    db_data = db_response.json()
    
    data_sources = db_data.get("data_sources", [])
    data_source_id = data_sources[0]["id"]
    
    # 步骤 2: 使用 data_source_id 查询
    while has_more:
        query_url = (
            "https://api.notion.com/v1/data_sources/"
            f"{data_source_id}/query"
        )
        response = self.client.client.post(
            query_url, json=body, headers=headers
        )
        # 处理响应...
    return results
```

## 影响范围

以下方法会间接受到影响（调用 `query_all()` 的方法）：

- `get_all_book()` - 获取所有书籍
- `check_existing_books()` - 检查书籍是否存在

## 测试

运行以下命令测试修复：

```bash
python test_multi_source.py
```

预期输出：
```
初始化 NotionHelper...
✓ 初始化成功
  书架数据库 ID: xxx...
  
测试 query_all 方法...
✓ 成功获取 N 本书籍
  第一本书: xxx...
```

## 兼容性说明

- ✅ 适用于新的 Notion API (2025-09-03)
- ✅ 自动处理多数据源情况
- ✅ 向后兼容 (处理了错误情况)

## 相关链接

- [Notion API 文档](https://developers.notion.com/reference)
- [数据库查询 API](https://developers.notion.com/reference/post-database-query)
- [数据源 API](https://developers.notion.com/reference/post-data-source-query)
