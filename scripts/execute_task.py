#!/usr/bin/env python3
"""
WoodenMan 项目背景色修改任务执行脚本
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    print("🚀 执行 WoodenMan 背景色修改任务")
    print("=" * 40)

    # 解析项目根目录
    project_root = Path(__file__).resolve().parents[1]
    venv_python = project_root / "venv" / "bin" / "python"
    config_path = project_root / ".aider-automation.json"

    # 目标项目路径（保留为环境可配置，默认原路径如存在，否则提示）
    woodenman_path = os.environ.get("WOODENMAN_PATH", "/Users/zy/Developer/WoodenMan")

    # 检查路径是否存在
    if not os.path.exists(woodenman_path):
        print(f"❌ 错误: WoodenMan 目录不存在: {woodenman_path}")
        return 1

    if not venv_python.exists():
        print(f"❌ 错误: 虚拟环境 Python 不存在: {venv_python}")
        return 1

    if not config_path.exists():
        print(f"❌ 错误: 配置文件不存在: {config_path}")
        return 1

    print(f"📁 切换到目录: {woodenman_path}")
    os.chdir(woodenman_path)

    # 构建命令
    cmd = [
        str(venv_python),
        "-m", "aider_automation.main",
        "--config", str(config_path),
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