#!/usr/bin/env python3
"""
测试不同的 DeepSeek 模型名称格式
"""

import subprocess
import os
import tempfile

def test_model_name(model_name, api_key):
    """测试特定的模型名称"""
    print(f"\n🧪 测试模型名称: {model_name}")

    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('# Test file\nprint("Hello, World!")\n')
        test_file = f.name

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['DEEPSEEK_API_KEY'] = api_key

        # 构建测试命令
        cmd = [
            'aider',
            '--model', model_name,
            '--no-pretty',
            '--yes',
            '--message', 'Add a comment to this file',
            test_file
        ]

        print(f"执行命令: {' '.join(cmd[:6])}...")

        # 执行命令，设置较短的超时时间
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode == 0:
            print(f"✅ 模型 {model_name} 工作正常")
            return True
        else:
            print(f"❌ 模型 {model_name} 失败")
            if result.stderr:
                print(f"错误信息: {result.stderr[:200]}...")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ 模型 {model_name} 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试 {model_name} 时出错: {e}")
        return False
    finally:
        # 清理临时文件
        try:
            os.unlink(test_file)
        except:
            pass

def main():
    print("🚀 DeepSeek 模型名称测试工具")
    print("=" * 50)

    # 从配置文件读取 API Key
    api_key = "sk-967f84ada6b2448eba5a1e6b0a385e78"  # 你的 API Key

    if not api_key:
        print("❌ 未找到 API Key")
        return

    # 测试不同的模型名称格式
    model_names = [
        "deepseek-chat",
        "deepseek/deepseek-chat",
        "deepseek-coder",
        "deepseek/deepseek-coder",
        "deepseek",
        "openai/deepseek-chat",  # 通过 OpenAI 兼容接口
    ]

    working_models = []

    for model_name in model_names:
        if test_model_name(model_name, api_key):
            working_models.append(model_name)

    print("\n" + "=" * 50)
    print("📊 测试结果:")

    if working_models:
        print("✅ 可用的模型名称:")
        for model in working_models:
            print(f"   - {model}")
        print(f"\n💡 建议使用: {working_models[0]}")
    else:
        print("❌ 没有找到可用的模型名称")
        print("\n🔧 可能的解决方案:")
        print("1. 检查 API Key 是否正确")
        print("2. 检查网络连接")
        print("3. 尝试使用 OpenAI 兼容格式")
        print("4. 更新 aider 到最新版本")

if __name__ == "__main__":
    main()