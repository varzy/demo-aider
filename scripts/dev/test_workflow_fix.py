#!/usr/bin/env python3
"""
测试工作流程修复
"""

import subprocess
import os

def test_workflow():
    print("🧪 测试修复后的工作流程...")

    # 切换到 WoodenMan 目录
    woodenman_path = "/Users/zy/Developer/WoodenMan"
    os.chdir(woodenman_path)

    # 首先切换到 main 分支
    print("📂 切换到 main 分支...")
    subprocess.run(["git", "checkout", "main"], capture_output=True)

    # 运行 aider-automation
    python_path = "/Users/zy/Developer/demo-aider/venv/bin/python"
    config_path = "/Users/zy/Developer/demo-aider/.aider-automation.json"

    cmd = [
        python_path,
        "-m", "aider_automation.main",
        "--config", config_path,
        "为 static/index.html 添加一个简单的页脚，包含版权信息"
    ]

    print("🚀 执行 aider-automation...")
    print("命令:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, timeout=180)

        if result.returncode == 0:
            print("🎉 工作流程执行成功！")

            # 检查结果
            print("\n📊 检查执行结果:")

            # 检查当前分支
            branch_result = subprocess.run(["git", "branch", "--show-current"],
                                         capture_output=True, text=True)
            if branch_result.returncode == 0:
                print(f"当前分支: {branch_result.stdout.strip()}")

            # 检查最近的提交
            log_result = subprocess.run(["git", "log", "-1", "--oneline"],
                                      capture_output=True, text=True)
            if log_result.returncode == 0:
                print(f"最近提交: {log_result.stdout.strip()}")

            return True
        else:
            print(f"❌ 工作流程失败，退出码: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ 工作流程执行超时")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

if __name__ == "__main__":
    test_workflow()