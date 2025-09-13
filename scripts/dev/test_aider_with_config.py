#!/usr/bin/env python3
"""
使用配置文件 API Key 的 aider 测试脚本
"""

import subprocess
import os
from pathlib import Path
import json

def test_aider_config():
    print("🔍 测试 aider 配置...")

    project_root = Path(__file__).resolve().parents[2]
    config_path = str(project_root / ".aider-automation.json")

    # 检查配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        api_key = config.get('aider', {}).get('api_key')
        model = config.get('aider', {}).get('model')

        print(f"📋 配置的模型: {model}")

        if api_key and api_key != "请在这里填入你的_DEEPSEEK_API_KEY":
            print("✅ 配置文件中已设置 API Key")
        else:
            print("❌ 配置文件中未设置有效的 API Key")
            print("请在 .aider-automation.json 中设置正确的 api_key")
            return False

    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
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

    return True

def run_woodenman_task_with_automation():
    """使用 aider-automation 运行 WoodenMan 任务"""
    if not test_aider_config():
        return

    print("\n🚀 使用 aider-automation 执行 WoodenMan 任务...")

    # 切换到 WoodenMan 目录
    woodenman_path = Path(os.environ.get("WOODENMAN_PATH", "/Users/zy/Developer/WoodenMan"))
    os.chdir(str(woodenman_path))

    # 使用 aider-automation
    python_path = str(project_root / "venv" / "bin" / "python")
    config_path = str(project_root / ".aider-automation.json")

    cmd = [
        python_path,
        "-m", "aider_automation.main",
        "--config", config_path,
        "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"
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
    run_woodenman_task_with_automation()