#!/usr/bin/env python3
"""
Aider 诊断脚本 - 检查配置和环境问题
"""

import subprocess
import json
import os
import sys

def check_aider_version():
    """检查 aider 版本"""
    print("🔍 检查 aider 版本...")
    try:
        result = subprocess.run(["aider", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Aider 版本: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Aider 版本检查失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 无法运行 aider: {e}")
        return False

def check_model_config():
    """检查模型配置"""
    print("\n🔍 检查模型配置...")

    config_path = "/Users/zy/Developer/demo-aider/.aider-automation.json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        model = config.get('aider', {}).get('model')
        print(f"📋 当前配置的模型: {model}")

        # 检查常见的 DeepSeek 模型名称
        valid_deepseek_models = [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek/deepseek-chat",
            "deepseek/deepseek-coder"
        ]

        if model in valid_deepseek_models:
            print(f"✅ 模型名称看起来正确")
        else:
            print(f"⚠️  模型名称可能有问题，建议使用: {valid_deepseek_models}")

        return config

    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None

def test_aider_command():
    """测试 aider 命令"""
    print("\n🔍 测试 aider 命令...")

    # 测试基本的 aider 命令
    test_commands = [
        ["aider", "--help"],
        ["aider", "--models"],
    ]

    for cmd in test_commands:
        try:
            print(f"🚀 执行: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print(f"✅ 命令执行成功")
                if "--models" in cmd:
                    # 检查是否包含 deepseek 模型
                    if "deepseek" in result.stdout.lower():
                        print("✅ 找到 DeepSeek 模型支持")
                    else:
                        print("⚠️  未找到 DeepSeek 模型支持")
            else:
                print(f"❌ 命令执行失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"⏰ 命令执行超时")
        except Exception as e:
            print(f"❌ 命令执行错误: {e}")

def check_environment_variables():
    """检查环境变量"""
    print("\n🔍 检查环境变量...")

    important_vars = [
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "GITHUB_TOKEN",
        "PATH"
    ]

    for var in important_vars:
        value = os.environ.get(var)
        if value:
            if "KEY" in var or "TOKEN" in var:
                print(f"✅ {var}: {'*' * 10} (已设置)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未设置")

def suggest_fixes():
    """建议修复方案"""
    print("\n💡 建议的修复方案:")
    print("1. 更新模型配置为 'deepseek-chat'")
    print("2. 确保设置了 DEEPSEEK_API_KEY 环境变量")
    print("3. 检查 aider 是否为最新版本: pip install --upgrade aider-chat")
    print("4. 尝试使用完整的模型名称: 'deepseek/deepseek-chat'")

def main():
    print("🚀 Aider 诊断工具")
    print("=" * 50)

    # 检查各个组件
    aider_ok = check_aider_version()
    config = check_model_config()

    if aider_ok:
        test_aider_command()

    check_environment_variables()

    print("\n" + "=" * 50)
    suggest_fixes()

    # 生成修复后的配置
    if config:
        print("\n📝 建议的配置文件内容:")
        config['aider']['model'] = 'deepseek-chat'
        print(json.dumps(config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()