"""分支策略和命名管理"""

import re
import hashlib
from datetime import datetime
from typing import Optional
from pathlib import Path

from .git_manager import GitManager
from .exceptions import GitOperationError


class BranchStrategy:
    """分支策略管理器"""

    def __init__(self, git_manager: GitManager, branch_prefix: str = "aider-automation/"):
        """
        初始化分支策略管理器

        Args:
            git_manager: Git 管理器实例
            branch_prefix: 分支名称前缀
        """
        self.git_manager = git_manager
        self.branch_prefix = branch_prefix

    def generate_branch_name(self, prompt: str, base_name: Optional[str] = None) -> str:
        """
        生成分支名称

        Args:
            prompt: 用户提示词
            base_name: 基础分支名称（可选）

        Returns:
            str: 生成的分支名称
        """
        if base_name:
            # 使用用户指定的基础名称
            clean_name = self._sanitize_branch_name(base_name)
        else:
            # 从提示词生成分支名称
            clean_name = self._generate_name_from_prompt(prompt)

        # 添加时间戳确保唯一性
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # 组合完整分支名称
        full_name = f"{self.branch_prefix}{clean_name}-{timestamp}"

        # 确保分支名称长度合理（Git 分支名称限制）
        if len(full_name) > 250:
            # 截断并添加哈希确保唯一性
            hash_suffix = hashlib.md5(full_name.encode()).hexdigest()[:8]
            max_length = 250 - len(hash_suffix) - 1
            full_name = full_name[:max_length] + "-" + hash_suffix

        return full_name

    def create_unique_branch(self, prompt: str, base_name: Optional[str] = None) -> str:
        """
        创建唯一的分支

        Args:
            prompt: 用户提示词
            base_name: 基础分支名称（可选）

        Returns:
            str: 创建的分支名称

        Raises:
            GitOperationError: 分支创建失败
        """
        branch_name = self.generate_branch_name(prompt, base_name)

        # 检查分支是否已存在，如果存在则生成新名称
        attempt = 0
        original_name = branch_name

        while self._branch_exists(branch_name) and attempt < 10:
            attempt += 1
            # 在原名称基础上添加序号
            branch_name = f"{original_name}-{attempt}"

        if attempt >= 10:
            raise GitOperationError(
                f"无法生成唯一分支名称，尝试了 {attempt} 次",
                "请手动指定分支名称"
            )

        # 创建分支
        self.git_manager.create_branch(branch_name)

        return branch_name

    def handle_branch_conflict(self, branch_name: str, prompt: str) -> str:
        """
        处理分支冲突

        Args:
            branch_name: 冲突的分支名称
            prompt: 用户提示词

        Returns:
            str: 解决冲突后的分支名称

        Raises:
            GitOperationError: 无法解决冲突
        """
        if not self._branch_exists(branch_name):
            # 分支不存在，直接创建
            self.git_manager.create_branch(branch_name)
            return branch_name

        # 分支已存在，检查是否可以切换
        try:
            current_branch = self.git_manager.get_current_branch()

            if current_branch == branch_name:
                # 已经在目标分支上
                return branch_name

            # 检查是否有未提交的更改
            if self.git_manager.has_changes():
                raise GitOperationError(
                    f"分支 '{branch_name}' 已存在，且当前有未提交的更改",
                    "请先提交或暂存当前更改，或使用不同的分支名称"
                )

            # 切换到现有分支
            self.git_manager.switch_branch(branch_name)
            return branch_name

        except GitOperationError as e:
            # 如果是因为有未提交更改导致的错误，直接重新抛出
            if "未提交的更改" in str(e):
                raise e
            # 其他错误，生成新分支名称
            new_branch_name = self.create_unique_branch(prompt)
            return new_branch_name

    def _generate_name_from_prompt(self, prompt: str) -> str:
        """
        从提示词生成分支名称

        Args:
            prompt: 用户提示词

        Returns:
            str: 生成的分支名称
        """
        # 提取关键词
        words = re.findall(r'\b\w+\b', prompt.lower())

        # 过滤常见停用词
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'must', 'shall', 'this', 'that', 'these', 'those',
            '的', '了', '在', '是', '有', '和', '与', '或', '但', '如果', '因为', '所以'
        }

        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]

        # 取前3-5个有意义的词
        selected_words = meaningful_words[:5] if len(meaningful_words) >= 3 else meaningful_words[:3]

        if not selected_words:
            # 如果没有有意义的词，使用默认名称
            return "feature"

        # 连接词语
        name = "-".join(selected_words)

        # 限制长度
        if len(name) > 50:
            name = name[:50]

        return self._sanitize_branch_name(name)

    def _sanitize_branch_name(self, name: str) -> str:
        """
        清理分支名称，确保符合 Git 分支命名规范

        Args:
            name: 原始名称

        Returns:
            str: 清理后的名称
        """
        # Git 分支命名规则：
        # - 不能包含空格
        # - 不能以 . 开头或结尾
        # - 不能包含 ..
        # - 不能包含特殊字符如 ~, ^, :, ?, *, [, \
        # - 不能以 / 结尾

        # 替换空格和特殊字符为连字符
        name = re.sub(r'[^\w\-_/]', '-', name)

        # 移除连续的连字符
        name = re.sub(r'-+', '-', name)

        # 移除开头和结尾的连字符、点和斜杠
        name = name.strip('-._/')

        # 确保不为空
        if not name:
            name = "feature"

        # 确保不以点开头
        if name.startswith('.'):
            name = 'branch-' + name[1:]

        return name

    def _branch_exists(self, branch_name: str) -> bool:
        """
        检查分支是否存在

        Args:
            branch_name: 分支名称

        Returns:
            bool: 分支是否存在
        """
        try:
            return self.git_manager._branch_exists(branch_name)
        except Exception:
            return False