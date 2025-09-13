#!/usr/bin/env python3
"""
测试修复后的配置
"""

import subprocess
import os
import json

def test_aider_config():
    print("🔍 测试修复后的 aider 配置...")

    config_path = "/Users/zy/Developer/demo-aider/.aider-automation.json"

    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    model = config['aider']['model']
    options = config['aider']['options']

    print(f"📋 配置的模型: {model}")
    print(f"📋 配置的选项: {options}")

    # 检查是否包含 API Key 设置
    has_api_key = any("--api-key" in str(opt) for opt in options)
    if has_api_key:
        print("✅ 找到 API Key 配置")
    else:
        print("❌ 未找到 API Key 配置")
        return False

    return True

def test_direct_aider_command():
    """直接测试 aider 命令"""
    print("\n🧪 测试直接 aider 命令...")

    # 切换到 WoodenMan 目录
    woodenman_path = "/Users/zy/Developer/WoodenMan"
    os.chdir(woodenman_path)

    # 构建测试命令
    cmd = [
        "aider",
        "--model", "deepseek/deepseek-chat",
        "--api-key", "deepseek=sk-967f84ada6b2448eba5a1e6b0a385e78",
        "--no-pretty",
        "--yes",
        "--message", "Add a comment '// Test comment' to the top of index.html if it exists"
    ]

    print(f"执行命令: aider --model deepseek/deepseek-chat --api-key deepseek=*** --no-pretty --yes --message '...'")

    try:
        result = subprocess.run(cmd, timeout=60, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 直接 aider 命令执行成功！")
            print("输出:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            return True
        else:
            print(f"❌ 直接 aider 命令失败，退出码: {result.returncode}")
            print("错误:", result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("⏰ 直接 aider 命令超时")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

def test_automation_command():
    """测试 aider-automation 命令"""
    print("\n🚀 测试 aider-automation 命令...")

    # 切换到 WoodenMan 目录
    woodenman_path = "/Users/zy/Developer/WoodenMan"
    os.chdir(woodenman_path)

    python_path = "/Users/zy/Developer/demo-aider/venv/bin/python"
    config_path = "/Users/zy/Developer/demo-aider/.aider-automation.json"

    cmd = [
        python_path,
        "-m", "aider_automation.main",
        "--config", config_path,
        "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"
    ]

    print("执行 aider-automation 命令...")

    try:
        result = subprocess.run(cmd, timeout=120)

        if result.returncode == 0:
            print("🎉 aider-automation 执行成功！")
            return True
        else:
            print(f"❌ aider-automation 失败，退出码: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ aider-automation 超时")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

def main():
    print("🚀 测试修复后的配置")
    print("=" * 50)

    # 测试配置
    if not test_aider_config():
        return

    # 测试直接命令
    if test_direct_aider_command():
        print("\n✅ 直接 aider 命令工作正常，现在测试 automation...")
        test_automation_command()
    else:
        print("\n❌ 直接 aider 命令失败，请检查配置")

if __name__ == "__main__":
    main()