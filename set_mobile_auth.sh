#!/bin/bash
# 设置微信读书移动端认证信息
# 从抓包工具中获取这些值

echo "设置微信读书移动端认证信息..."
echo ""

# 默认值（原来的认证信息）
DEFAULT_VID="300063969"
DEFAULT_SKEY="kvqQmWwa"

echo "📋 当前默认认证信息:"
echo "   vid: $DEFAULT_VID"
echo "   skey: $DEFAULT_SKEY"
echo ""

# 询问用户是否要更新（只在交互式shell中）
if [[ -t 0 && -t 1 ]]; then
    read -p "是否要更新认证信息？(y/N): " UPDATE_CHOICE
else
    # 非交互式环境，默认不更新
    UPDATE_CHOICE="n"
    echo "非交互式环境，自动使用默认认证信息"
fi

if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
    echo ""
    echo "📖 更新认证信息获取方法："
    echo "1. 在手机上安装抓包工具（如Charles、mitmproxy等）"
    echo "2. 配置手机代理到电脑"
    echo "3. 在微信读书App中进行操作"
    echo "4. 抓取 https://i.weread.qq.com/readdata/detail 的请求"
    echo "5. 从请求头中提取 vid 和 skey 的值"
    echo ""

    # 请用户输入新的值
    read -p "请输入新的 vid 值: " NEW_VID
    read -p "请输入新的 skey 值: " NEW_SKEY

    if [ -z "$NEW_VID" ] || [ -z "$NEW_SKEY" ]; then
        echo "❌ vid 和 skey 不能为空，使用默认值"
        VID="$DEFAULT_VID"
        SKEY="$DEFAULT_SKEY"
    else
        VID="$NEW_VID"
        SKEY="$NEW_SKEY"
        echo "✅ 使用新的认证信息"
    fi
else
    echo "✅ 使用默认认证信息"
    VID="$DEFAULT_VID"
    SKEY="$DEFAULT_SKEY"
fi

# 设置环境变量
export WEREAD_VID="$VID"
export WEREAD_SKEY="$SKEY"

echo ""
echo "🔑 环境变量已设置:"
echo "WEREAD_VID=$WEREAD_VID"
echo "WEREAD_SKEY=$WEREAD_SKEY"
echo ""
echo "🧪 现在可以运行测试:"
echo "python tests/test_new_get_api_data.py"
echo ""
echo "💡 提示：每次重启终端都需要重新运行此脚本"