#!/bin/bash

# WoodenMan 项目背景色修改任务执行脚本
# 修复版本 - 解决命令格式问题（动态解析路径）

echo "🚀 WoodenMan 项目背景色修改任务"
echo "=================================================="

# 解析项目根目录（scripts/dev/ 的上两级）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 路径变量（支持通过环境变量覆盖）
DEMO_AIDER_PATH="${DEMO_AIDER_PATH:-$PROJECT_ROOT}"
WOODENMAN_PATH="${WOODENMAN_PATH:-/Users/zy/Developer/WoodenMan}"
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
    echo "   请确保在项目根目录中有正确的配置文件"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 显示将要执行的信息
echo "📁 目标项目: $WOODENMAN_PATH"
echo "🐍 Python 解释器: $VENV_PYTHON"
echo "⚙️  配置文件: $CONFIG_FILE"
echo "🎯 任务: 修改 index.html 背景色为淡蓝色"
echo ""

# 切换到 WoodenMan 目录
echo "📂 切换到 WoodenMan 目录..."
cd "$WOODENMAN_PATH" || {
    echo "❌ 错误: 无法切换到 WoodenMan 目录"
    exit 1
}

echo "✅ 当前目录: $(pwd)"
echo ""

# 检查项目文件
echo "📋 检查项目文件..."
if [ -f "static/index.html" ]; then
    echo "✅ 找到 static/index.html"
elif [ -f "index.html" ]; then
    echo "✅ 找到 index.html"
else
    echo "⚠️  未找到 index.html，aider 将创建新文件"
fi

# 检查 Git 状态
echo "📋 检查 Git 状态..."
if git status >/dev/null 2>&1; then
    echo "✅ Git 仓库状态正常"
    echo "   当前分支: $(git branch --show-current)"
else
    echo "❌ 错误: 不是有效的 Git 仓库"
    exit 1
fi

echo ""
echo "🚀 开始执行任务..."
echo "=================================================="

# 执行 aider-automation 命令
# 注意：这里使用正确的命令格式，避免之前的语法错误
"$VENV_PYTHON" -m aider_automation.main \
    --config "$CONFIG_FILE" \
    --verbose \
    "将 static/index.html 的背景色改为淡蓝色 (#e3f2fd)，保持现有的 HTML 结构和其他样式不变"

# 检查执行结果
EXIT_CODE=$?

echo ""
echo "=================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "🎉 任务执行成功！"
    echo ""
    echo "📋 后续步骤："
    echo "1. 检查修改的文件: git diff"
    echo "2. 在浏览器中查看效果: open static/index.html"
    echo "3. 查看创建的 PR: 检查命令输出中的 GitHub 链接"
    echo ""
else
    echo "❌ 任务执行失败，退出码: $EXIT_CODE"
    echo ""
    echo "🔧 可能的解决方案："
    echo "1. 检查 GitHub Token 是否正确设置"
    echo "2. 检查网络连接"
    echo "3. 检查 aider 是否正确安装"
    echo "4. 查看详细错误信息"
    echo ""
fi

exit $EXIT_CODE