#!/usr/bin/env python3
"""
检查 Aider Automation 配置和环境
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (未找到)")
        return False


def check_command(command, description):
    """检查命令是否可用"""
    try:
        result = subprocess.run([command, "--version"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ {description}: {version}")
            return True
        else:
            print(f"❌ {description}: 命令执行失败")
            return False
    except FileNotFoundError:
        print(f"❌ {description}: 命令未找到")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description}: 命令超时")
        return False
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False


def check_config():
    """检查配置文件"""
    config_file = Path(".aider-automation.json")

    if not config_file.exists():
        print("❌ 配置文件: .aider-automation.json (未找到)")
        print("   请运行: python setup.py")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print("✅ 配置文件: .aider-automation.json")

        # 检查必需字段
        issues = []

        if 'github' not in config:
            issues.append("缺少 github 配置")
        else:
            github = config['github']
            if 'repo' not in github or github['repo'] == 'owner/repository-name':
                issues.append("需要设置正确的 GitHub 仓库")

            if 'token' not in github:
                issues.append("缺少 GitHub token 配置")

        if issues:
            print("   ⚠️  配置问题:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print("   ✅ 配置格式正确")
            return True

    except json.JSONDecodeError as e:
        print(f"❌ 配置文件: JSON 格式错误 - {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件: 读取失败 - {e}")
        return False


def check_github_token():
    """检查 GitHub Token"""
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        print("❌ GitHub Token: 环境变量 GITHUB_TOKEN 未设置")
        print("   请运行: export GITHUB_TOKEN='你的_token'")
        return False

    if not token.startswith('ghp_') and not token.startswith('github_pat_'):
        print("⚠️  GitHub Token: Token 格式可能不正确")
        print("   GitHub Token 通常以 'ghp_' 或 'github_pat_' 开头")

    print(f"✅ GitHub Token: 已设置 ({token[:10]}...)")
    return True


def main():
    print("🔍 Aider Automation 环境检查")
    print("=" * 40)

    all_good = True

    print("\n📁 文件检查:")
    all_good &= check_file_exists(".aider-automation.json", "配置文件")

    print("\n⚙️  配置检查:")
    all_good &= check_config()

    print("\n🔑 环境变量检查:")
    all_good &= check_github_token()

    print("\n🛠️  工具检查:")
    all_good &= check_command("python", "Python")
    all_good &= check_command("git", "Git")
    all_good &= check_command("aider", "Aider")

    print("\n📦 Python 包检查:")
    try:
        import click
        print("✅ Click: 已安装")
    except ImportError:
        print("❌ Click: 未安装")
        all_good = False

    try:
        import requests
        print("✅ Requests: 已安装")
    except ImportError:
        print("❌ Requests: 未安装")
        all_good = False

    try:
        import rich
        print("✅ Rich: 已安装")
    except ImportError:
        print("❌ Rich: 未安装")
        all_good = False

    print("\n" + "=" * 40)

    if all_good:
        print("🎉 所有检查通过！你可以开始使用 aider-automation 了")
        print("\n💡 使用示例:")
        print("   python -m aider_automation.main '添加一个 hello world 函数'")
    else:
        print("❌ 发现问题，请根据上面的提示进行修复")
        print("\n🔧 常见解决方案:")
        print("   1. 运行设置脚本: python setup.py")
        print("   2. 安装依赖: pip install -e '.[dev]'")
        print("   3. 安装 aider: pip install aider-chat")
        print("   4. 设置 GitHub Token: export GITHUB_TOKEN='你的_token'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 检查已取消")
    except Exception as e:
        print(f"\n❌ 检查过程中出现错误: {e}")
        sys.exit(1)