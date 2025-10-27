# 微信读书移动端认证设置指南

## 背景说明

微信读书的新API (`https://i.weread.qq.com/readdata/detail`) 需要移动端的认证信息，而不是网页端的cookie。

## 获取认证信息的方法

### 方法1: 使用抓包工具
1. 在手机上安装抓包工具（如Charles、mitmproxy等）
2. 配置手机代理到电脑
3. 在微信读书App中进行操作
4. 抓取 `https://i.weread.qq.com/readdata/detail` 的请求
5. 从请求头中提取 `vid` 和 `skey` 的值

### 方法2: 从App存储中提取
- iOS: 使用工具查看微信读书App的数据存储
- Android: 查看App的数据目录

## 设置认证信息

### 方式1: 使用环境变量
```bash
export WEREAD_VID="你的vid值"
export WEREAD_SKEY="你的skey值"
```

### 方式2: 使用设置脚本
```bash
./set_mobile_auth.sh
```

### 方式3: 直接在代码中设置
修改 `weread2notionpro/weread_api.py` 中的 `get_readtiming_detail_data` 方法：
```python
# 直接设置认证信息
vid = "你的vid值"
skey = "你的skey值"
```

## 测试验证

设置好认证信息后，运行测试：
```bash
python tests/test_new_get_api_data.py
```

成功时应该看到：
```
✅ 详细API 调用成功
📊 阅读数据点数: X
总阅读时间: XXX 分钟
```

## 注意事项

1. 移动端认证信息可能有有效期，需要定期更新
2. 不同设备和账户的认证信息不同
3. 确保使用最新版本的微信读书App进行抓包

## API数据结构

新API返回的完整数据结构：
- `readTimes`: 日期时间戳 -> 阅读分钟数
- `readDays`: 总阅读天数
- `totalReadTime`: 总阅读时间(分钟)
- `yearReport`: 年度报告数据
- `preferBooks`: 偏好书籍列表
- `preferCategory`: 偏好分类统计
- `preferAuthor`: 偏好作者统计
- `medals`: 勋章成就
- `readStat`: 阅读统计概览
- `shareInfo`: 分享信息