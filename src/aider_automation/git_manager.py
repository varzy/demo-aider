"""Git 操作管理器"""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse
import re

from .exceptions import GitOperationError


class GitManager:
    """Git 操作管理器"""

    def __init__(self, repo_path: str = "."):
        """
        初始化 Git 管理器

        Args:
            repo_path: Git 仓库路径，默认为当前目录
        """
        self.repo_path = Path(repo_path).resolve()

    def create_branch(self, branch_name: str) -> bool:
        """
        创建新分支

        Args:
            branch_name: 分支名称

        Returns:
            bool: 是否创建成功

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            # 检查分支是否已存在
            if self._branch_exists(branch_name):
                raise GitOperationError(
                    f"分支 '{branch_name}' 已存在",
                    "请使用不同的分支名称或删除现有分支"
                )

            # 创建并切换到新分支
            result = self._run_git_command(["checkout", "-b", branch_name])

            if result.returncode != 0:
                raise GitOperationError(
                    f"创建分支失败: {result.stderr}",
                    "请检查分支名称是否有效"
                )

            return True
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def switch_branch(self, branch_name: str) -> bool:
        """
        切换到指定分支

        Args:
            branch_name: 分支名称

        Returns:
            bool: 是否切换成功

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            # 检查分支是否存在
            if not self._branch_exists(branch_name):
                raise GitOperationError(
                    f"分支 '{branch_name}' 不存在",
                    "请先创建分支或检查分支名称"
                )

            # 切换分支
            result = self._run_git_command(["checkout", branch_name])

            if result.returncode != 0:
                raise GitOperationError(
                    f"切换分支失败: {result.stderr}",
                    "请检查工作目录是否有未提交的更改"
                )

            return True
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def has_changes(self) -> bool:
        """
        检查是否有未提交的更改

        Returns:
            bool: 是否有更改

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            # 检查工作目录状态
            result = self._run_git_command(["status", "--porcelain"])

            if result.returncode != 0:
                raise GitOperationError(
                    f"检查 Git 状态失败: {result.stderr}"
                )

            return bool(result.stdout.strip())
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def get_changed_files(self) -> List[str]:
        """
        获取已更改的文件列表

        Returns:
            List[str]: 更改的文件列表

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            result = self._run_git_command(["status", "--porcelain"])

            if result.returncode != 0:
                raise GitOperationError(
                    f"获取更改文件失败: {result.stderr}"
                )

            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # 解析 git status --porcelain 输出格式
                    # 格式: XY filename (前两个字符是状态码，后面是文件名)
                    if len(line) > 2:
                        # 跳过前两个状态字符，然后去除前导空格
                        filename = line[2:].lstrip()
                        if filename:
                            files.append(filename)

            return files
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def add_all_changes(self) -> bool:
        """
        添加所有更改到暂存区

        Returns:
            bool: 是否添加成功

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            result = self._run_git_command(["add", "."])

            if result.returncode != 0:
                raise GitOperationError(
                    f"添加文件到暂存区失败: {result.stderr}"
                )

            return True
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def commit_changes(self, message: str, allow_empty: bool = False) -> str:
        """
        提交更改

        Args:
            message: 提交信息
            allow_empty: 是否允许空提交

        Returns:
            str: 提交哈希

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            if not message.strip():
                raise GitOperationError(
                    "提交信息不能为空",
                    "请提供有意义的提交信息"
                )

            # 构建提交命令
            commit_cmd = ["commit", "-m", message]
            if allow_empty:
                commit_cmd.append("--allow-empty")

            # 提交更改
            result = self._run_git_command(commit_cmd)

            if result.returncode != 0:
                raise GitOperationError(
                    f"提交失败: {result.stderr}",
                    "请检查是否有文件在暂存区"
                )

            # 获取提交哈希
            hash_result = self._run_git_command(["rev-parse", "HEAD"])

            if hash_result.returncode != 0:
                raise GitOperationError(
                    f"获取提交哈希失败: {hash_result.stderr}"
                )

            return hash_result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def push_branch(self, branch_name: str, remote: str = "origin") -> bool:
        """
        推送分支到远程仓库

        Args:
            branch_name: 分支名称
            remote: 远程仓库名称，默认为 origin

        Returns:
            bool: 是否推送成功

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            # 推送分支
            result = self._run_git_command(["push", "-u", remote, branch_name])

            if result.returncode != 0:
                raise GitOperationError(
                    f"推送分支失败: {result.stderr}",
                    "请检查远程仓库配置和网络连接"
                )

            return True
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def get_current_branch(self) -> str:
        """
        获取当前分支名称

        Returns:
            str: 当前分支名称

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            result = self._run_git_command(["branch", "--show-current"])

            if result.returncode != 0:
                raise GitOperationError(
                    f"获取当前分支失败: {result.stderr}"
                )

            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def get_remote_url(self, remote: str = "origin") -> str:
        """
        获取远程仓库 URL

        Args:
            remote: 远程仓库名称，默认为 origin

        Returns:
            str: 远程仓库 URL

        Raises:
            GitOperationError: Git 操作失败
        """
        try:
            result = self._run_git_command(["remote", "get-url", remote])

            if result.returncode != 0:
                raise GitOperationError(
                    f"获取远程仓库 URL 失败: {result.stderr}",
                    f"请检查远程仓库 '{remote}' 是否存在"
                )

            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise GitOperationError(f"Git 命令执行失败: {e}")

    def get_repo_info(self) -> Tuple[str, str]:
        """
        从远程 URL 解析仓库信息

        Returns:
            Tuple[str, str]: (owner, repo) 元组

        Raises:
            GitOperationError: 解析失败
        """
        try:
            remote_url = self.get_remote_url()

            # 解析 GitHub URL
            # 支持 HTTPS 和 SSH 格式
            if remote_url.startswith("https://github.com/"):
                # HTTPS: https://github.com/owner/repo.git
                path = urlparse(remote_url).path
                match = re.match(r'^/([^/]+)/([^/]+?)(?:\.git)?/?$', path)
            elif remote_url.startswith("git@github.com:"):
                # SSH: git@github.com:owner/repo.git
                match = re.match(r'^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$', remote_url)
            else:
                raise GitOperationError(
                    f"不支持的远程 URL 格式: {remote_url}",
                    "仅支持 GitHub HTTPS 和 SSH URL"
                )

            if not match:
                raise GitOperationError(
                    f"无法解析仓库信息: {remote_url}",
                    "请检查远程 URL 格式"
                )

            owner, repo = match.groups()
            return owner, repo
        except GitOperationError:
            raise
        except Exception as e:
            raise GitOperationError(f"解析仓库信息失败: {e}")

    def _branch_exists(self, branch_name: str) -> bool:
        """
        检查分支是否存在

        Args:
            branch_name: 分支名称

        Returns:
            bool: 分支是否存在
        """
        try:
            result = self._run_git_command(["branch", "--list", branch_name])
            return bool(result.stdout.strip())
        except subprocess.SubprocessError:
            return False

    def _run_git_command(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        运行 Git 命令

        Args:
            args: Git 命令参数
            timeout: 超时时间（秒）

        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        cmd = ["git"] + args

        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=timeout
        )