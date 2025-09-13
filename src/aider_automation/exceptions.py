"""自定义异常类定义"""

from typing import Optional


class AiderAutomationError(Exception):
    """基础异常类"""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ConfigurationError(AiderAutomationError):
    """配置相关错误"""
    pass


class DependencyError(AiderAutomationError):
    """依赖项缺失或不可用"""
    pass


class GitOperationError(AiderAutomationError):
    """Git 操作失败"""
    pass


class AiderExecutionError(AiderAutomationError):
    """Aider 执行失败"""
    pass


class GitHubAPIError(AiderAutomationError):
    """GitHub API 调用失败"""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        self.status_code = status_code
        super().__init__(message, details)