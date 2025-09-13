"""GitHub 集成器"""

import requests
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .models import Config, PRResult, AiderResult
from .exceptions import GitHubAPIError


class GitHubIntegrator:
    """GitHub 集成器"""

    def __init__(self, config: Config):
        """
        初始化 GitHub 集成器

        Args:
            config: 配置对象
        """
        self.config = config
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {config.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "aider-automation/0.1.0"
        })

    def create_pull_request(
        self,
        branch_name: str,
        title: str,
        body: str,
        base_branch: Optional[str] = None
    ) -> PRResult:
        """
        创建 Pull Request

        Args:
            branch_name: 源分支名称
            title: PR 标题
            body: PR 描述
            base_branch: 目标分支，默认使用配置中的默认分支

        Returns:
            PRResult: PR 创建结果
        """
        try:
            if base_branch is None:
                base_branch = self.config.default_branch

            # 验证仓库信息
            owner, repo = self._parse_repo_info()

            # 构建 PR 数据
            pr_data = {
                "title": title,
                "body": body,
                "head": branch_name,
                "base": base_branch
            }

            # 发送创建 PR 请求
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            response = self._make_request("POST", url, json=pr_data)

            if response.status_code == 201:
                pr_info = response.json()
                return PRResult(
                    success=True,
                    pr_url=pr_info["html_url"],
                    pr_number=pr_info["number"]
                )
            else:
                error_msg = self._extract_error_message(response)
                return PRResult(
                    success=False,
                    error_message=f"创建 PR 失败 (状态码: {response.status_code}): {error_msg}"
                )

        except GitHubAPIError as e:
            return PRResult(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return PRResult(
                success=False,
                error_message=f"创建 PR 时发生未知错误: {e}"
            )

    def get_repository_info(self) -> Dict[str, Any]:
        """
        获取仓库信息

        Returns:
            Dict[str, Any]: 仓库信息

        Raises:
            GitHubAPIError: API 调用失败
        """
        try:
            owner, repo = self._parse_repo_info()
            url = f"{self.base_url}/repos/{owner}/{repo}"

            response = self._make_request("GET", url)

            if response.status_code == 200:
                return response.json()
            else:
                error_msg = self._extract_error_message(response)
                raise GitHubAPIError(
                    f"获取仓库信息失败: {error_msg}",
                    response.status_code
                )

        except requests.RequestException as e:
            raise GitHubAPIError(f"网络请求失败: {e}")

    def validate_access(self) -> bool:
        """
        验证 GitHub API 访问权限

        Returns:
            bool: 是否有访问权限
        """
        try:
            # 测试基本 API 访问
            response = self._make_request("GET", f"{self.base_url}/user")

            if response.status_code != 200:
                return False

            # 测试仓库访问权限
            owner, repo = self._parse_repo_info()
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self._make_request("GET", repo_url)

            return response.status_code == 200

        except Exception:
            return False

    def check_branch_exists(self, branch_name: str) -> bool:
        """
        检查分支是否存在于远程仓库

        Args:
            branch_name: 分支名称

        Returns:
            bool: 分支是否存在
        """
        try:
            owner, repo = self._parse_repo_info()
            url = f"{self.base_url}/repos/{owner}/{repo}/branches/{branch_name}"

            response = self._make_request("GET", url)
            return response.status_code == 200

        except Exception:
            return False

    def format_pr_body(self, aider_result: AiderResult, prompt: str) -> str:
        """
        格式化 PR 描述

        Args:
            aider_result: Aider 执行结果
            prompt: 原始提示词

        Returns:
            str: 格式化的 PR 描述
        """
        template = self.config.pr_body_template

        # 格式化修改的文件列表
        if aider_result.modified_files:
            modified_files_str = "\n".join(f"- {file}" for file in aider_result.modified_files)
        else:
            modified_files_str = "无文件修改记录"

        # 替换模板变量
        formatted_body = template.format(
            prompt=prompt,
            modified_files=modified_files_str,
            aider_summary=aider_result.summary or "无摘要信息"
        )

        return formatted_body

    def format_pr_title(self, aider_result: AiderResult, prompt: str) -> str:
        """
        格式化 PR 标题

        Args:
            aider_result: Aider 执行结果
            prompt: 原始提示词

        Returns:
            str: 格式化的 PR 标题
        """
        template = self.config.pr_title_template

        # 使用 aider 摘要或提示词作为摘要
        summary = aider_result.summary or prompt[:50]
        if len(summary) > 50:
            summary = summary[:47] + "..."

        # 替换模板变量
        formatted_title = template.format(
            summary=summary,
            prompt=prompt
        )

        # 确保标题长度合理
        if len(formatted_title) > 100:
            formatted_title = formatted_title[:97] + "..."

        return formatted_title

    def _parse_repo_info(self) -> tuple[str, str]:
        """
        解析仓库信息

        Returns:
            tuple[str, str]: (owner, repo) 元组

        Raises:
            GitHubAPIError: 解析失败
        """
        repo_str = self.config.github_repo

        if '/' not in repo_str:
            raise GitHubAPIError(
                f"无效的仓库格式: {repo_str}",
                details="仓库格式应为 'owner/repo'"
            )

        parts = repo_str.split('/')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise GitHubAPIError(
                f"无效的仓库格式: {repo_str}",
                details="仓库格式应为 'owner/repo'"
            )

        return parts[0], parts[1]

    def _make_request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        **kwargs
    ) -> requests.Response:
        """
        发送 HTTP 请求，包含重试逻辑

        Args:
            method: HTTP 方法
            url: 请求 URL
            max_retries: 最大重试次数
            **kwargs: 其他请求参数

        Returns:
            requests.Response: 响应对象

        Raises:
            GitHubAPIError: 请求失败
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, timeout=30, **kwargs)

                # 检查速率限制
                if response.status_code == 429:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    current_time = int(time.time())
                    wait_time = max(reset_time - current_time, 60)  # 至少等待 60 秒

                    if attempt < max_retries:
                        time.sleep(min(wait_time, 300))  # 最多等待 5 分钟
                        continue
                    else:
                        raise GitHubAPIError(
                            "GitHub API 速率限制",
                            429,
                            f"请等待 {wait_time} 秒后重试"
                        )

                return response

            except requests.RequestException as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    break

        # 所有重试都失败了
        raise GitHubAPIError(
            f"GitHub API 请求失败: {last_exception}",
            details=f"已重试 {max_retries} 次"
        )

    def _extract_error_message(self, response: requests.Response) -> str:
        """
        从响应中提取错误信息

        Args:
            response: HTTP 响应

        Returns:
            str: 错误信息
        """
        try:
            error_data = response.json()

            if isinstance(error_data, dict):
                # GitHub API 标准错误格式
                if 'message' in error_data:
                    message = error_data['message']

                    # 添加详细错误信息
                    if 'errors' in error_data:
                        errors = error_data['errors']
                        if isinstance(errors, list) and errors:
                            error_details = []
                            for error in errors:
                                if isinstance(error, dict) and 'message' in error:
                                    error_details.append(error['message'])
                            if error_details:
                                message += f" 详细信息: {'; '.join(error_details)}"

                    return message

                # 其他格式的错误
                return str(error_data)

            return str(error_data)

        except (ValueError, KeyError):
            # JSON 解析失败，返回原始文本
            return response.text or f"HTTP {response.status_code}"