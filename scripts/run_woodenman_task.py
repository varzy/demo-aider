#!/usr/bin/env python3
"""
WoodenMan 项目背景色修改任务执行脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 开始执行 WoodenMan 项目背景色修改任务")
    print("=" * 50)

    # 项目根目录
    demo_aider_path = Path(__file__).resolve().parents[1]
    # 目标项目路径可通过环境变量覆盖
    woodenman_path = Path(os.environ.get("WOODENMAN_PATH", "/Users/zy/Developer/WoodenMan"))

    # 检查路径是否存在
    if not demo_aider_path.exists():
        print(f"❌ 错误: demo-aider 目录不存在: {demo_aider_path}")
        return False

    if not woodenman_path.exists():
        print(f"❌ 错误: WoodenMan 目录不存在: {woodenman_path}")
        return False

    # 检查虚拟环境
    venv_python = demo_aider_path / "venv" / "bin" / "python"
    if not venv_python.exists():
        print(f"❌ 错误: 虚拟环境 Python 不存在: {venv_python}")
        return False

    # 检查配置文件
    config_file = demo_aider_path / ".aider-automation.json"
    if not config_file.exists():
        print(f"❌ 错误: 配置文件不存在: {config_file}")
        return False

    # 检查 WoodenMan 项目文件
    index_html = woodenman_path / "index.html"
    if not index_html.exists():
        print(f"⚠️  警告: index.html 文件不存在: {index_html}")
        print("   aider 可能会创建这个文件")

    print("✅ 所有检查通过，开始执行任务...")
    print()

    # 构建命令
    cmd = [
        str(venv_python),
        "-m", "aider_automation.main",
        "--config", str(config_file),
        "将 index.html 的背景色改为淡蓝色 (#e3f2fd)，如果文件不存在请创建一个简单的 HTML 页面"
    ]

    print(f"📋 执行命令: {' '.join(cmd)}")
    print(f"📁 工作目录: {woodenman_path}")
    print()

    try:
        # 切换到 WoodenMan 目录并执行命令
        result = subprocess.run(
            cmd,
            cwd=str(woodenman_path),
            capture_output=False,  # 让输出直接显示
            text=True
        )

        if result.returncode == 0:
            print("\n🎉 任务执行成功！")
            return True
        else:
            print(f"\n❌ 任务执行失败，退出码: {result.returncode}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 命令执行失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 任务被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 脚本执行失败: {e}")
        sys.exit(1)