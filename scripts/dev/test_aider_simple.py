#!/usr/bin/env python3
"""
简单的 aider 测试脚本
"""

import subprocess
import os
from pathlib import Path

def test_aider():
    print("🔍 测试 aider 配置...")

    # 检查环境变量
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    if deepseek_key:
        print("✅ DEEPSEEK_API_KEY 已设置")
    else:
        print("❌ DEEPSEEK_API_KEY 未设置")
        print("请运行: export DEEPSEEK_API_KEY='你的_api_key'")
        return False

    # 测试 aider 版本
    try:
        result = subprocess.run(["aider", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Aider 版本: {result.stdout.strip()}")
        else:
            print(f"❌ Aider 版本检查失败")
            return False
    except Exception as e:
        print(f"❌ 无法运行 aider: {e}")
        return False

    # 测试模型列表
    try:
        result = subprocess.run(["aider", "--models"], capture_output=True, text=True, timeout=30)
        if "deepseek" in result.stdout.lower():
            print("✅ DeepSeek 模型可用")
        else:
            print("⚠️  DeepSeek 模型可能不可用")
    except Exception as e:
        print(f"⚠️  无法检查模型列表: {e}")

    return True

def run_woodenman_task():
    """运行 WoodenMan 任务"""
    if not test_aider():
        return

    print("\n🚀 执行 WoodenMan 任务...")

    # 切换到 WoodenMan 目录（支持环境变量 WOODENMAN_PATH）
    woodenman_path = Path(os.environ.get("WOODENMAN_PATH", "/Users/zy/Developer/WoodenMan"))
    os.chdir(str(woodenman_path))

    # 构建命令
    cmd = [
        "aider",
        "--model", "deepseek-chat",
        "--no-pretty",
        "--yes",
        "--message", "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"
    ]

    print(f"执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, timeout=300)
        if result.returncode == 0:
            print("🎉 任务执行成功！")
        else:
            print(f"❌ 任务执行失败，退出码: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("⏰ 任务执行超时")
    except Exception as e:
        print(f"❌ 执行错误: {e}")

if __name__ == "__main__":
    run_woodenman_task()