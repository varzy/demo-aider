"""依赖项检查器"""

import shutil
import subprocess
from typing import List, Optional
import requests

from .models import Config
from .exceptions import DependencyError


class DependencyChecker:
    """依赖项检查器"""

    def __init__(self):
        """初始化依赖项检查器"""
        pass

    def check_aider(self) -> bool:
        """
        检查 aider 工具是否可用

        Returns:
            bool: aider 是否可用
        """
        try:
            # 检查 aider 命令是否存在
            if not shutil.which("aider"):
                return False

            # 尝试运行 aider --version 来验证
            result = subprocess.run(
                ["aider", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def check_git(self) -> bool:
        """
        检查 Git 是否可用

        Returns:
            bool: Git 是否可用
        """
        try:
            # 检查 git 命令是否存在
            if not shutil.which("git"):
                return False

            # 尝试运行 git --version 来验证
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def check_github_access(self, token: str) -> bool:
        """
        检查 GitHub API 访问权限

        Args:
            token: GitHub API token

        Returns:
            bool: GitHub API 是否可访问
        """
        try:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # 测试 GitHub API 访问
            response = requests.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10
            )

            return response.status_code == 200
        except (requests.RequestException, requests.Timeout):
            return False

    def check_git_repository(self) -> bool:
        """
        检查当前目录是否为 Git 仓库

        Returns:
            bool: 是否为 Git 仓库
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def check_git_remote(self) -> bool:
        """
        检查 Git 仓库是否有远程仓库

        Returns:
            bool: 是否有远程仓库
        """
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.returncode == 0 and bool(result.stdout.strip())
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False

    def check_all_dependencies(self, config: Config) -> List[str]:
        """
        检查所有依赖项

        Args:
            config: 配置对象

        Returns:
            List[str]: 缺失或不可用的依赖项列表
        """
        missing_deps = []

        # 检查 aider
        if not self.check_aider():
            missing_deps.append("aider - AI 编程助手工具未安装或不可用")

        # 检查 git
        if not self.check_git():
            missing_deps.append("git - Git 版本控制工具未安装或不可用")
        else:
            # 如果 git 可用，进一步检查仓库状态
            if not self.check_git_repository():
                missing_deps.append("git-repo - 当前目录不是 Git 仓库")
            elif not self.check_git_remote():
                missing_deps.append("git-remote - Git 仓库没有配置远程仓库")

        # 检查 GitHub 访问
        if not self.check_github_access(config.github_token):
            missing_deps.append("github-access - GitHub API 访问失败，请检查 token 是否有效")

        return missing_deps

    def get_dependency_info(self) -> dict:
        """
        获取依赖项详细信息

        Returns:
            dict: 依赖项信息字典
        """
        info = {}

        # Aider 信息
        if self.check_aider():
            try:
                result = subprocess.run(
                    ["aider", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                info["aider"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.returncode == 0 else "unknown"
                }
            except Exception:
                info["aider"] = {"available": False, "version": None}
        else:
            info["aider"] = {"available": False, "version": None}

        # Git 信息
        if self.check_git():
            try:
                result = subprocess.run(
                    ["git", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                info["git"] = {
                    "available": True,
                    "version": result.stdout.strip() if result.returncode == 0 else "unknown",
                    "repository": self.check_git_repository(),
                    "remote": self.check_git_remote()
                }
            except Exception:
                info["git"] = {"available": False, "version": None}
        else:
            info["git"] = {"available": False, "version": None}

        return info

    def validate_environment(self, config: Config) -> None:
        """
        验证环境并抛出详细错误

        Args:
            config: 配置对象

        Raises:
            DependencyError: 依赖项检查失败
        """
        missing_deps = self.check_all_dependencies(config)

        if missing_deps:
            error_message = "以下依赖项缺失或不可用:\n" + "\n".join(f"- {dep}" for dep in missing_deps)

            suggestions = []

            if any("aider" in dep for dep in missing_deps):
                suggestions.append("安装 aider: pip install aider-chat")

            if any("git" in dep for dep in missing_deps):
                suggestions.append("安装 Git: https://git-scm.com/downloads")
                suggestions.append("初始化 Git 仓库: git init")
                suggestions.append("添加远程仓库: git remote add origin <url>")

            if any("github-access" in dep for dep in missing_deps):
                suggestions.append("检查 GitHub token 是否有效")
                suggestions.append("确保 token 有足够的权限")
                suggestions.append("检查网络连接")

            details = "建议解决方案:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)

            raise DependencyError(error_message, details)