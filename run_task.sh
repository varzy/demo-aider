#!/bin/bash

# WoodenMan 项目背景色修改任务执行脚本

echo "🚀 开始执行 WoodenMan 项目背景色修改任务"
echo "=================================================="

# 设置路径
DEMO_AIDER_PATH="/Users/zy/Developer/demo-aider"
WOODENMAN_PATH="/Users/zy/Developer/WoodenMan"

# 检查路径
if [ ! -d "$DEMO_AIDER_PATH" ]; then
    echo "❌ 错误: demo-aider 目录不存在: $DEMO_AIDER_PATH"
    exit 1
fi

if [ ! -d "$WOODENMAN_PATH" ]; then
    echo "❌ 错误: WoodenMan 目录不存在: $WOODENMAN_PATH"
    exit 1
fi

# 检查虚拟环境
VENV_PYTHON="$DEMO_AIDER_PATH/venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 错误: 虚拟环境 Python 不存在: $VENV_PYTHON"
    exit 1
fi

# 检查配置文件
CONFIG_FILE="$DEMO_AIDER_PATH/.aider-automation.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

echo "✅ 所有检查通过，开始执行任务..."
echo ""

# 切换到 WoodenMan 目录
cd "$WOODENMAN_PATH" || exit 1

echo "📁 当前工作目录: $(pwd)"
echo "📋 执行 aider-automation..."
echo ""

# 执行任务
"$VENV_PYTHON" -m aider_automation.main \
    --config "$CONFIG_FILE" \
    "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果文件不存在请创建一个简单的 HTML 页面"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 任务执行成功！"
else
    echo ""
    echo "❌ 任务执行失败"
    exit 1
fi