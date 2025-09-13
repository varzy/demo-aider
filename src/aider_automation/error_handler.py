"""错误处理和报告"""

import traceback
from typing import List, Optional, Dict, Any
from .exceptions import (
    AiderAutomationError,
    ConfigurationError,
    DependencyError,
    GitOperationError,
    AiderExecutionError,
    GitHubAPIError
)
from .logger import Logger


class ErrorHandler:
    """错误处理器"""

    def __init__(self, logger: Logger):
        """
        初始化错误处理器

        Args:
            logger: 日志管理器
        """
        self.logger = logger

    def handle_error(self, error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """
        处理错误并生成报告

        Args:
            error: 异常对象
            context: 错误上下文

        Returns:
            Dict[str, Any]: 错误报告
        """
        error_report = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "suggestions": [],
            "recovery_actions": [],
            "severity": "error"
        }

        # 根据错误类型提供特定的建议
        if isinstance(error, ConfigurationError):
            error_report.update(self._handle_configuration_error(error))
        elif isinstance(error, DependencyError):
            error_report.update(self._handle_dependency_error(error))
        elif isinstance(error, GitOperationError):
            error_report.update(self._handle_git_error(error))
        elif isinstance(error, AiderExecutionError):
            error_report.update(self._handle_aider_error(error))
        elif isinstance(error, GitHubAPIError):
            error_report.update(self._handle_github_error(error))
        else:
            error_report.update(self._handle_generic_error(error))

        # 记录错误
        self._log_error(error_report)

        return error_report

    def _handle_configuration_error(self, error: ConfigurationError) -> Dict[str, Any]:
        """处理配置错误"""
        suggestions = []
        recovery_actions = []

        error_msg = str(error).lower()

        if "配置文件不存在" in error_msg:
            suggestions.extend([
                "运行 'aider-automation --init' 创建默认配置文件",
                "检查配置文件路径是否正确",
                "确保有足够的文件系统权限"
            ])
            recovery_actions.append("create_default_config")

        elif "github token" in error_msg or "token" in error_msg:
            suggestions.extend([
                "检查 GitHub token 是否正确设置",
                "确保 token 有足够的权限",
                "验证环境变量 GITHUB_TOKEN 是否存在"
            ])
            recovery_actions.append("validate_github_token")

        elif "仓库格式" in error_msg:
            suggestions.extend([
                "确保仓库格式为 'owner/repo'",
                "检查仓库名称是否正确",
                "验证仓库是否存在且可访问"
            ])
            recovery_actions.append("validate_repo_format")

        elif "json" in error_msg:
            suggestions.extend([
                "检查配置文件的 JSON 语法",
                "使用 JSON 验证工具检查格式",
                "重新创建配置文件"
            ])
            recovery_actions.append("validate_json_syntax")

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _handle_dependency_error(self, error: DependencyError) -> Dict[str, Any]:
        """处理依赖项错误"""
        suggestions = []
        recovery_actions = []

        error_msg = str(error).lower()

        if "aider" in error_msg:
            suggestions.extend([
                "安装 aider: pip install aider-chat",
                "确保 aider 在 PATH 环境变量中",
                "检查 aider 版本是否兼容"
            ])
            recovery_actions.append("install_aider")

        if "git" in error_msg:
            suggestions.extend([
                "安装 Git: https://git-scm.com/downloads",
                "确保 Git 在 PATH 环境变量中",
                "初始化 Git 仓库: git init"
            ])
            recovery_actions.append("install_git")

        if "github" in error_msg or "api" in error_msg:
            suggestions.extend([
                "检查网络连接",
                "验证 GitHub token 权限",
                "确保仓库存在且可访问"
            ])
            recovery_actions.append("check_github_access")

        if "仓库" in error_msg and "不是" in error_msg:
            suggestions.extend([
                "在项目根目录运行: git init",
                "添加远程仓库: git remote add origin <url>",
                "确保在正确的项目目录中"
            ])
            recovery_actions.append("init_git_repo")

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _handle_git_error(self, error: GitOperationError) -> Dict[str, Any]:
        """处理 Git 操作错误"""
        suggestions = []
        recovery_actions = []

        error_msg = str(error).lower()

        if "分支" in error_msg and "已存在" in error_msg:
            suggestions.extend([
                "使用不同的分支名称",
                "切换到现有分支: git checkout <branch>",
                "删除现有分支: git branch -D <branch>"
            ])
            recovery_actions.append("handle_branch_conflict")

        elif "分支" in error_msg and "不存在" in error_msg:
            suggestions.extend([
                "检查分支名称是否正确",
                "创建新分支: git checkout -b <branch>",
                "查看可用分支: git branch -a"
            ])
            recovery_actions.append("create_branch")

        elif "未提交的更改" in error_msg:
            suggestions.extend([
                "提交当前更改: git commit -am 'message'",
                "暂存更改: git stash",
                "丢弃更改: git checkout -- ."
            ])
            recovery_actions.append("handle_uncommitted_changes")

        elif "推送" in error_msg:
            suggestions.extend([
                "检查网络连接",
                "验证远程仓库权限",
                "拉取最新更改: git pull origin <branch>"
            ])
            recovery_actions.append("retry_push")

        elif "提交" in error_msg:
            suggestions.extend([
                "检查是否有文件在暂存区",
                "添加文件到暂存区: git add .",
                "确保提交信息不为空"
            ])
            recovery_actions.append("prepare_commit")

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _handle_aider_error(self, error: AiderExecutionError) -> Dict[str, Any]:
        """处理 Aider 执行错误"""
        suggestions = []
        recovery_actions = []

        error_msg = str(error).lower()

        if "找不到" in error_msg or "not found" in error_msg:
            suggestions.extend([
                "安装 aider: pip install aider-chat",
                "检查 aider 是否在 PATH 中",
                "重新安装 aider"
            ])
            recovery_actions.append("install_aider")

        elif "超时" in error_msg or "timeout" in error_msg:
            suggestions.extend([
                "检查网络连接",
                "增加超时时间",
                "重试执行"
            ])
            recovery_actions.append("retry_with_timeout")

        elif "权限" in error_msg or "permission" in error_msg:
            suggestions.extend([
                "检查文件权限",
                "以管理员身份运行",
                "确保有写入权限"
            ])
            recovery_actions.append("check_permissions")

        elif "模型" in error_msg or "model" in error_msg:
            suggestions.extend([
                "检查 AI 模型配置",
                "验证 API 密钥",
                "尝试使用不同的模型"
            ])
            recovery_actions.append("check_model_config")

        else:
            suggestions.extend([
                "检查 aider 日志输出",
                "验证项目文件结构",
                "尝试简化提示词"
            ])
            recovery_actions.append("debug_aider")

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _handle_github_error(self, error: GitHubAPIError) -> Dict[str, Any]:
        """处理 GitHub API 错误"""
        suggestions = []
        recovery_actions = []

        if hasattr(error, 'status_code'):
            status_code = error.status_code

            if status_code == 401:
                suggestions.extend([
                    "检查 GitHub token 是否有效",
                    "重新生成 GitHub token",
                    "确保 token 没有过期"
                ])
                recovery_actions.append("refresh_github_token")

            elif status_code == 403:
                suggestions.extend([
                    "检查 token 权限范围",
                    "确保有仓库访问权限",
                    "检查是否触发了速率限制"
                ])
                recovery_actions.append("check_github_permissions")

            elif status_code == 404:
                suggestions.extend([
                    "检查仓库名称是否正确",
                    "确保仓库存在且可访问",
                    "验证分支名称"
                ])
                recovery_actions.append("verify_repo_exists")

            elif status_code == 422:
                suggestions.extend([
                    "检查请求数据格式",
                    "确保分支间有差异",
                    "验证 PR 参数"
                ])
                recovery_actions.append("validate_pr_data")

            elif status_code == 429:
                suggestions.extend([
                    "等待速率限制重置",
                    "减少 API 调用频率",
                    "使用不同的 token"
                ])
                recovery_actions.append("wait_rate_limit")

        error_msg = str(error).lower()

        if "网络" in error_msg or "network" in error_msg:
            suggestions.extend([
                "检查网络连接",
                "尝试使用代理",
                "稍后重试"
            ])
            recovery_actions.append("check_network")

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _handle_generic_error(self, error: Exception) -> Dict[str, Any]:
        """处理通用错误"""
        suggestions = [
            "检查错误详情和堆栈跟踪",
            "查看日志文件获取更多信息",
            "尝试重新运行命令",
            "如果问题持续，请报告 bug"
        ]

        recovery_actions = ["retry", "check_logs"]

        return {
            "suggestions": suggestions,
            "recovery_actions": recovery_actions,
            "severity": "error"
        }

    def _log_error(self, error_report: Dict[str, Any]):
        """记录错误到日志"""
        self.logger.print_error_details(
            Exception(error_report["message"]),
            error_report["suggestions"]
        )

        # 记录详细错误信息到调试日志
        self.logger.debug(f"错误报告: {error_report}")


def format_exception_details(error: Exception, include_traceback: bool = False) -> str:
    """
    格式化异常详情

    Args:
        error: 异常对象
        include_traceback: 是否包含堆栈跟踪

    Returns:
        str: 格式化的异常信息
    """
    details = [f"错误类型: {type(error).__name__}"]
    details.append(f"错误信息: {str(error)}")

    if hasattr(error, 'details') and error.details:
        details.append(f"详细信息: {error.details}")

    if hasattr(error, 'status_code') and error.status_code:
        details.append(f"状态码: {error.status_code}")

    if include_traceback:
        details.append("堆栈跟踪:")
        details.append(traceback.format_exc())

    return "\n".join(details)


def get_error_suggestions(error: Exception) -> List[str]:
    """
    获取错误建议

    Args:
        error: 异常对象

    Returns:
        List[str]: 建议列表
    """
    from .logger import get_logger

    logger = get_logger()
    handler = ErrorHandler(logger)
    error_report = handler.handle_error(error)

    return error_report.get("suggestions", [])