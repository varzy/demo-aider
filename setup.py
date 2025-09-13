#!/usr/bin/env python3
"""
Aider Automation 设置脚本
帮助用户快速配置项目
"""

import json
import os
import sys
from pathlib import Path


def main():
    print("🚀 欢迎使用 Aider Automation 设置向导！")
    print("=" * 50)

    # 检查配置文件
    config_file = Path(".aider-automation.json")
    if config_file.exists():
        print(f"✅ 发现现有配置文件: {config_file}")
        overwrite = input("是否要重新配置？(y/N): ").lower().strip()
        if overwrite != 'y':
            print("设置已取消")
            return

    print("\n📝 请提供以下信息：")

    # 获取 GitHub 仓库信息
    print("\n1. GitHub 仓库信息")
    print("   格式：用户名/仓库名 (例如: zyqfork/my-project)")
    repo = input("   请输入你的 GitHub 仓库: ").strip()

    if not repo or '/' not in repo:
        print("❌ 错误：仓库格式不正确，应该是 '用户名/仓库名'")
        return

    # 获取 GitHub Token
    print("\n2. GitHub Token")
    print("   你可以选择：")
    print("   a) 使用环境变量 GITHUB_TOKEN (推荐)")
    print("   b) 直接输入 token")

    token_choice = input("   选择 (a/b): ").lower().strip()

    if token_choice == 'b':
        token = input("   请输入你的 GitHub Token: ").strip()
        if not token:
            print("❌ 错误：Token 不能为空")
            return
    else:
        token = "${GITHUB_TOKEN}"
        print("   ✅ 将使用环境变量 GITHUB_TOKEN")

    # 获取 AI 模型选择
    print("\n3. AI 模型选择")
    print("   可选模型：")
    print("   1) gpt-4 (推荐，但需要 OpenAI API)")
    print("   2) gpt-3.5-turbo (更便宜)")
    print("   3) claude-3-sonnet (Anthropic)")
    print("   4) 不指定 (使用 aider 默认)")

    model_choice = input("   选择 (1-4): ").strip()
    model_map = {
        '1': 'gpt-4',
        '2': 'gpt-3.5-turbo',
        '3': 'claude-3-sonnet',
        '4': None
    }
    model = model_map.get(model_choice)

    # 获取分支设置
    print("\n4. Git 分支设置")
    default_branch = input("   默认分支名称 (默认: main): ").strip() or "main"
    branch_prefix = input("   分支前缀 (默认: aider-automation/): ").strip() or "aider-automation/"

    # 创建配置
    config = {
        "github": {
            "token": token,
            "repo": repo
        },
        "aider": {
            "options": ["--no-pretty", "--yes"]
        },
        "git": {
            "default_branch": default_branch,
            "branch_prefix": branch_prefix
        },
        "templates": {
            "commit_message": "feat: {summary}",
            "pr_title": "AI-generated changes: {summary}",
            "pr_body": "## 自动生成的更改\\n\\n**提示词：** {prompt}\\n\\n**修改的文件：**\\n{modified_files}\\n\\n**Aider 摘要：**\\n{aider_summary}"
        }
    }

    if model:
        config["aider"]["model"] = model

    # 保存配置文件
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 配置文件已保存到: {config_file}")

        # 显示下一步
        print("\n🎯 下一步操作：")

        if token == "${GITHUB_TOKEN}":
            print("1. 设置环境变量：")
            print(f"   export GITHUB_TOKEN='你的_github_token'")
            print("   (或添加到 ~/.zshrc 文件中)")

        print("2. 检查配置：")
        print("   python -m aider_automation.main --check")

        print("3. 开始使用：")
        print("   python -m aider_automation.main '你的提示词'")

        print("\n📚 更多信息请查看:")
        print("   - README.md")
        print("   - 配置指南.md")

    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return

    print("\n🎉 设置完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 设置已取消")
    except Exception as e:
        print(f"\n❌ 设置过程中出现错误: {e}")
        sys.exit(1)