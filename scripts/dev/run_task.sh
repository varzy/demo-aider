#!/bin/bash

# 解析项目根目录（scripts/dev/ 的上两级）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 设置变量（允许环境变量覆盖）
WOODENMAN_PATH="${WOODENMAN_PATH:-/Users/zy/Developer/WoodenMan}"
PYTHON_PATH="${PYTHON_PATH:-$PROJECT_ROOT/venv/bin/python}"
CONFIG_PATH="${CONFIG_PATH:-$PROJECT_ROOT/.aider-automation.json}"

echo "🚀 执行 WoodenMan 背景色修改任务"
echo "=================================="

# 切换到目标目录
cd "$WOODENMAN_PATH"

# 执行任务
"$PYTHON_PATH" -m aider_automation.main --config "$CONFIG_PATH" "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"

echo "任务执行完成！"