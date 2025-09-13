#!/usr/bin/env python3
"""
WoodenMan 项目背景色修改任务执行脚本
"""

import os
import subprocess
import sys

def main():
    print("🚀 执行 WoodenMan 背景色修改任务")
    print("=" * 40)

    # 设置路径
    woodenman_path = "/Users/zy/Developer/WoodenMan"
    python_path = "/Users/zy/Developer/demo-aider/venv/bin/python"
    config_path = "/Users/zy/Developer/demo-aider/.aider-automation.json"

    # 检查路径是否存在
    if not os.path.exists(woodenman_path):
        print(f"❌ 错误: WoodenMan 目录不存在: {woodenman_path}")
        return 1

    if not os.path.exists(python_path):
        print(f"❌ 错误: Python 解释器不存在: {python_path}")
        return 1

    if not os.path.exists(config_path):
        print(f"❌ 错误: 配置文件不存在: {config_path}")
        return 1

    print(f"📁 切换到目录: {woodenman_path}")
    os.chdir(woodenman_path)

    # 构建命令
    cmd = [
        python_path,
        "-m", "aider_automation.main",
        "--config", config_path,
        "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果需要请修改相关的 CSS 样式"
    ]

    print("🚀 执行命令...")
    print(f"命令: {' '.join(cmd)}")
    print()

    try:
        # 执行命令
        result = subprocess.run(cmd, check=True)
        print("\n🎉 任务执行成功！")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 任务执行失败，退出码: {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())