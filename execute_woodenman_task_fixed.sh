#!/bin/bash
# WoodenMan 项目背景色修改任务执行脚本
# 修复版本 - 解决命令格式问题

echo "🚀 开始执行 WoodenMan 项目背景色修改任务"
echo "=================================================="

# 设置路径变量
DEMO_AIDER_PATH="/Users/zy/Developer/demo-aider"
WOODENMAN_PATH="/Users/zy/Developer/WoodenMan"
VENV_PYTHON="$DEMO_AIDER_PATH/venv/bin/python"
CONFIG_FILE="$DEMO_AIDER_PATH/.aider-automation.json"

echo "📋 检查环境..."

# 检查 demo-aider 目录
if [ ! -d "$DEMO_AIDER_PATH" ]; then
    echo "❌ 错误: demo-aider 目录不存在: $DEMO_AIDER_PATH"
    exit 1
fi

# 检查 WoodenMan 目录
if [ ! -d "$WOODENMAN_PATH" ]; then
    echo "❌ 错误: WoodenMan 目录不存在: $WOODENMAN_PATH"
    exit 1
fi

# 检查虚拟环境 Python
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 错误: 虚拟环境 Python 不存在: $VENV_PYTHON"
    exit 1
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 检查 GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  警告: GITHUB_TOKEN 环境变量未设置"
    echo "   请运行: export GITHUB_TOKEN='你的_github_token'"
fi

echo "✅ 环境检查完成"
echo ""

# 显示将要执行的操作
echo "📁 目标目录: $WOODENMAN_PATH"
echo "🐍 Python 解释器: $VENV_PYTHON"
echo "⚙️  配置文件: $CONFIG_FILE"
echo "📝 任务: 将 index.html 的背景色改为淡蓝色"
echo ""

# 切换到 WoodenMan 目录
echo "📂 切换到 WoodenMan 目录..."
cd "$WOODENMAN_PATH" || {
    echo "❌ 错误: 无法切换到 WoodenMan 目录"
    exit 1
}

echo "✅ 当前工作目录: $(pwd)"
echo ""

# 检查 index.html 是否存在
if [ -f "index.html" ]; then
    echo "✅ 找到目标文件: index.html"
elif [ -f "static/index.html" ]; then
    echo "✅ 找到目标文件: static/index.html"
else
    echo "⚠️  目标文件 index.html 不存在，aider 可能会创建它"
fi

echo ""
echo "🚀 开始执行 aider-automation..."
echo "=================================================="

# 执行 aider-automation 命令 - 修复格式问题
"$VENV_PYTHON" -m aider_automation.main \
    --config "$CONFIG_FILE" \
    "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"

# 检查执行结果
EXIT_CODE=$?

echo ""
echo "=================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 任务执行成功！"
    echo ""
    echo "📊 执行结果检查:"

    # 检查 Git 状态
    echo "📋 Git 状态:"
    git status --short

    # 检查当前分支
    echo "🌿 当前分支:"
    git branch --show-current

    # 检查最近的提交
    echo "📝 最近的提交:"
    git log --oneline -1

    echo ""
    echo "💡 下一步操作:"
    echo "   1. 检查修改的文件内容"
    echo "   2. 在浏览器中测试 index.html"
    echo "   3. 查看 GitHub 上创建的 Pull Request"

else
    echo "❌ 任务执行失败 (退出码: $EXIT_CODE)"
    echo ""
    echo "🔧 可能的解决方案:"
    echo "   1. 检查 GitHub Token 是否正确设置"
    echo "   2. 检查网络连接"
    echo "   3. 检查 aider 和相关依赖是否正确安装"
    echo "   4. 查看上面的错误信息进行排查"
fi

exit $EXIT_CODE