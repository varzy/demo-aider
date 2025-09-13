"""Aider 执行器"""

import os
import subprocess
import re
from typing import List, Optional
from pathlib import Path

from .models import Config, AiderResult
from .exceptions import AiderExecutionError


class AiderExecutor:
    """Aider 执行器"""

    def __init__(self, config: Config, working_dir: str = "."):
        """
        初始化 Aider 执行器

        Args:
            config: 配置对象
            working_dir: 工作目录，默认为当前目录
        """
        self.config = config
        self.working_dir = Path(working_dir).resolve()

    def execute(self, prompt: str) -> AiderResult:
        """
        执行 aider 命令

        Args:
            prompt: 用户提示词

        Returns:
            AiderResult: 执行结果

        Raises:
            AiderExecutionError: 执行失败
        """
        try:
            if not prompt.strip():
                raise AiderExecutionError(
                    "提示词不能为空",
                    "请提供有意义的提示词"
                )

            # 构建命令
            command = self._build_command(prompt)

            # 执行命令
            result = self._run_aider_command(command)

            # 解析输出
            aider_result = self._parse_output(result, prompt)

            return aider_result

        except subprocess.SubprocessError as e:
            raise AiderExecutionError(f"Aider 命令执行失败: {e}")
        except Exception as e:
            raise AiderExecutionError(f"Aider 执行过程中发生错误: {e}")

    def _build_command(self, prompt: str) -> List[str]:
        """
        构建 aider 命令

        Args:
            prompt: 用户提示词

        Returns:
            List[str]: 命令参数列表
        """
        command = ["aider"]

        # 添加配置中的选项
        if self.config.aider.options:
            command.extend(self.config.aider.options)

        # 添加模型选项
        if self.config.aider.model:
            command.extend(["--model", self.config.aider.model])

        # 添加自动确认选项（避免交互）
        if "--yes" not in command and "-y" not in command:
            command.append("--yes")

        # 添加消息选项
        command.extend(["--message", prompt])

        return command

    def _run_aider_command(self, command: List[str], timeout: int = 300) -> subprocess.CompletedProcess:
        """
        运行 aider 命令

        Args:
            command: 命令参数列表
            timeout: 超时时间（秒），默认 5 分钟

        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        return subprocess.run(
            command,
            cwd=self.working_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def _parse_output(self, result: subprocess.CompletedProcess, prompt: str) -> AiderResult:
        """
        解析 aider 输出

        Args:
            result: 命令执行结果
            prompt: 原始提示词

        Returns:
            AiderResult: 解析后的结果
        """
        success = result.returncode == 0
        output = result.stdout + result.stderr

        if not success:
            return AiderResult(
                success=False,
                error_message=f"Aider 执行失败 (退出码: {result.returncode})",
                output=output
            )

        # 解析修改的文件
        modified_files = self._extract_modified_files(output)

        # 生成摘要
        summary = self._generate_summary(output, prompt, modified_files)

        return AiderResult(
            success=True,
            modified_files=modified_files,
            summary=summary,
            output=output
        )

    def _extract_modified_files(self, output: str) -> List[str]:
        """
        从 aider 输出中提取修改的文件列表

        Args:
            output: aider 输出

        Returns:
            List[str]: 修改的文件列表
        """
        modified_files = []

        # 匹配 aider 输出中的文件修改信息
        # 常见模式：
        # - "Modified: file.py"
        # - "Created: file.py"
        # - "Edited: file.py"
        # - "Added: file.py"

        patterns = [
            r'(?:Modified|Created|Edited|Added|Updated):\s*([^\s\n]+)',
            r'(?:修改|创建|编辑|添加|更新):\s*([^\s\n]+)',
            r'(?:✓|✔)\s*([^\s\n]+\.(?:py|js|ts|java|cpp|c|h|md|txt|json|yaml|yml|xml|html|css))',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                file_path = match.strip()
                if file_path and file_path not in modified_files:
                    modified_files.append(file_path)

        # 如果没有找到明确的文件修改信息，尝试从 git 状态中推断
        if not modified_files:
            # 查找可能的文件路径
            file_patterns = [
                r'([^\s\n]+\.(?:py|js|ts|java|cpp|c|h|md|txt|json|yaml|yml|xml|html|css))',
            ]

            for pattern in file_patterns:
                matches = re.findall(pattern, output)
                for match in matches:
                    file_path = match.strip()
                    # 简单验证文件路径的合理性
                    if (file_path and
                        not file_path.startswith('http') and
                        '/' not in file_path[:10] and  # 避免 URL
                        file_path not in modified_files):
                        modified_files.append(file_path)

        return modified_files[:10]  # 限制文件数量，避免误匹配过多

    def _generate_summary(self, output: str, prompt: str, modified_files: List[str]) -> str:
        """
        生成执行摘要

        Args:
            output: aider 输出
            prompt: 原始提示词
            modified_files: 修改的文件列表

        Returns:
            str: 执行摘要
        """
        # 尝试从 aider 输出中提取摘要信息
        summary_patterns = [
            r'(?:Summary|摘要):\s*(.+?)(?:\n|$)',
            r'(?:Changes made|所做更改):\s*(.+?)(?:\n|$)',
            r'(?:Completed|完成):\s*(.+?)(?:\n|$)',
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()

        # 如果没有找到明确的摘要，生成基于提示词和文件的摘要
        if modified_files:
            files_str = ", ".join(modified_files)
            return f"根据提示词修改了 {len(modified_files)} 个文件: {files_str}"
        else:
            return f"执行了提示词: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"

    def validate_environment(self) -> None:
        """
        验证 aider 执行环境

        Raises:
            AiderExecutionError: 环境验证失败
        """
        try:
            # 检查 aider 是否可用
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise AiderExecutionError(
                    "Aider 工具不可用",
                    "请确保 aider 已正确安装并在 PATH 中"
                )

        except subprocess.TimeoutExpired:
            raise AiderExecutionError(
                "Aider 版本检查超时",
                "请检查 aider 安装是否正常"
            )
        except FileNotFoundError:
            raise AiderExecutionError(
                "找不到 aider 命令",
                "请安装 aider: pip install aider-chat"
            )
        except Exception as e:
            raise AiderExecutionError(f"验证 aider 环境时发生错误: {e}")

    def get_aider_info(self) -> dict:
        """
        获取 aider 工具信息

        Returns:
            dict: aider 信息
        """
        try:
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {
                    "available": True,
                    "version": result.stdout.strip(),
                    "command": ["aider"] + self.config.aider.options
                }
            else:
                return {
                    "available": False,
                    "error": result.stderr.strip()
                }

        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }