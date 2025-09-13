"""测试错误处理器"""

from unittest.mock import MagicMock
import pytest

from aider_automation.error_handler import ErrorHandler, format_exception_details, get_error_suggestions
from aider_automation.exceptions import (
    ConfigurationError, DependencyError, GitOperationError,
    AiderExecutionError, GitHubAPIError
)
from aider_automation.logger import Logger


class TestErrorHandler:
    """测试错误处理器"""

    def setup_method(self):
        """设置测试方法"""
        self.mock_logger = MagicMock(spec=Logger)
        self.error_handler = ErrorHandler(self.mock_logger)

    def test_handle_configuration_error_missing_file(self):
        """测试处理配置文件不存在错误"""
        error = ConfigurationError("配置文件不存在")

        report = self.error_handler.handle_error(error)

        assert report["type"] == "ConfigurationError"
        assert "配置文件不存在" in report["message"]
        assert "create_default_config" in report["recovery_actions"]
        assert any("--init" in suggestion for suggestion in report["suggestions"])

    def test_handle_configuration_error_github_token(self):
        """测试处理 GitHub token 错误"""
        error = ConfigurationError("GitHub token 不能为空")

        report = self.error_handler.handle_error(error)

        assert "validate_github_token" in report["recovery_actions"]
        assert any("token" in suggestion.lower() for suggestion in report["suggestions"])

    def test_handle_configuration_error_repo_format(self):
        """测试处理仓库格式错误"""
        error = ConfigurationError("仓库格式错误")

        report = self.error_handler.handle_error(error)

        assert "validate_repo_format" in report["recovery_actions"]
        assert any("owner/repo" in suggestion for suggestion in report["suggestions"])

    def test_handle_configuration_error_json(self):
        """测试处理 JSON 格式错误"""
        error = ConfigurationError("JSON 格式错误")

        report = self.error_handler.handle_error(error)

        assert "validate_json_syntax" in report["recovery_actions"]
        assert any("JSON" in suggestion for suggestion in report["suggestions"])

    def test_handle_dependency_error_aider(self):
        """测试处理 aider 依赖错误"""
        error = DependencyError("aider 工具不可用")

        report = self.error_handler.handle_error(error)

        assert "install_aider" in report["recovery_actions"]
        assert any("pip install aider-chat" in suggestion for suggestion in report["suggestions"])

    def test_handle_dependency_error_git(self):
        """测试处理 Git 依赖错误"""
        error = DependencyError("git 工具不可用")

        report = self.error_handler.handle_error(error)

        assert "install_git" in report["recovery_actions"]
        assert any("git-scm.com" in suggestion for suggestion in report["suggestions"])

    def test_handle_dependency_error_github(self):
        """测试处理 GitHub 访问错误"""
        error = DependencyError("GitHub API 访问失败")

        report = self.error_handler.handle_error(error)

        assert "check_github_access" in report["recovery_actions"]
        assert any("网络连接" in suggestion for suggestion in report["suggestions"])

    def test_handle_dependency_error_git_repo(self):
        """测试处理 Git 仓库错误"""
        error = DependencyError("当前目录不是 Git 仓库")

        report = self.error_handler.handle_error(error)

        assert "init_git_repo" in report["recovery_actions"]
        assert any("git init" in suggestion for suggestion in report["suggestions"])

    def test_handle_git_error_branch_exists(self):
        """测试处理分支已存在错误"""
        error = GitOperationError("分支 'feature' 已存在")

        report = self.error_handler.handle_error(error)

        assert "handle_branch_conflict" in report["recovery_actions"]
        assert any("不同的分支名称" in suggestion for suggestion in report["suggestions"])

    def test_handle_git_error_branch_not_exists(self):
        """测试处理分支不存在错误"""
        error = GitOperationError("分支 'feature' 不存在")

        report = self.error_handler.handle_error(error)

        assert "create_branch" in report["recovery_actions"]
        assert any("checkout -b" in suggestion for suggestion in report["suggestions"])

    def test_handle_git_error_uncommitted_changes(self):
        """测试处理未提交更改错误"""
        error = GitOperationError("有未提交的更改")

        report = self.error_handler.handle_error(error)

        assert "handle_uncommitted_changes" in report["recovery_actions"]
        assert any("git commit" in suggestion for suggestion in report["suggestions"])

    def test_handle_git_error_push_failure(self):
        """测试处理推送失败错误"""
        error = GitOperationError("推送分支失败")

        report = self.error_handler.handle_error(error)

        assert "retry_push" in report["recovery_actions"]
        assert any("网络连接" in suggestion for suggestion in report["suggestions"])

    def test_handle_git_error_commit_failure(self):
        """测试处理提交失败错误"""
        error = GitOperationError("提交失败")

        report = self.error_handler.handle_error(error)

        assert "prepare_commit" in report["recovery_actions"]
        assert any("暂存区" in suggestion for suggestion in report["suggestions"])

    def test_handle_aider_error_not_found(self):
        """测试处理 aider 未找到错误"""
        error = AiderExecutionError("找不到 aider 命令")

        report = self.error_handler.handle_error(error)

        assert "install_aider" in report["recovery_actions"]
        assert any("pip install aider-chat" in suggestion for suggestion in report["suggestions"])

    def test_handle_aider_error_timeout(self):
        """测试处理 aider 超时错误"""
        error = AiderExecutionError("aider 执行超时")

        report = self.error_handler.handle_error(error)

        assert "retry_with_timeout" in report["recovery_actions"]
        assert any("网络连接" in suggestion for suggestion in report["suggestions"])

    def test_handle_aider_error_permission(self):
        """测试处理 aider 权限错误"""
        error = AiderExecutionError("权限被拒绝")

        report = self.error_handler.handle_error(error)

        assert "check_permissions" in report["recovery_actions"]
        assert any("文件权限" in suggestion for suggestion in report["suggestions"])

    def test_handle_aider_error_model(self):
        """测试处理 aider 模型错误"""
        error = AiderExecutionError("模型配置错误")

        report = self.error_handler.handle_error(error)

        assert "check_model_config" in report["recovery_actions"]
        assert any("模型配置" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_401(self):
        """测试处理 GitHub 401 错误"""
        error = GitHubAPIError("Unauthorized", status_code=401)

        report = self.error_handler.handle_error(error)

        assert "refresh_github_token" in report["recovery_actions"]
        assert any("token 是否有效" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_403(self):
        """测试处理 GitHub 403 错误"""
        error = GitHubAPIError("Forbidden", status_code=403)

        report = self.error_handler.handle_error(error)

        assert "check_github_permissions" in report["recovery_actions"]
        assert any("权限范围" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_404(self):
        """测试处理 GitHub 404 错误"""
        error = GitHubAPIError("Not Found", status_code=404)

        report = self.error_handler.handle_error(error)

        assert "verify_repo_exists" in report["recovery_actions"]
        assert any("仓库名称" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_422(self):
        """测试处理 GitHub 422 错误"""
        error = GitHubAPIError("Unprocessable Entity", status_code=422)

        report = self.error_handler.handle_error(error)

        assert "validate_pr_data" in report["recovery_actions"]
        assert any("请求数据格式" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_429(self):
        """测试处理 GitHub 429 错误"""
        error = GitHubAPIError("Rate Limit Exceeded", status_code=429)

        report = self.error_handler.handle_error(error)

        assert "wait_rate_limit" in report["recovery_actions"]
        assert any("速率限制" in suggestion for suggestion in report["suggestions"])

    def test_handle_github_error_network(self):
        """测试处理 GitHub 网络错误"""
        error = GitHubAPIError("网络连接失败")

        report = self.error_handler.handle_error(error)

        assert "check_network" in report["recovery_actions"]
        assert any("网络连接" in suggestion for suggestion in report["suggestions"])

    def test_handle_generic_error(self):
        """测试处理通用错误"""
        error = ValueError("Some generic error")

        report = self.error_handler.handle_error(error)

        assert report["type"] == "ValueError"
        assert "retry" in report["recovery_actions"]
        assert any("重新运行" in suggestion for suggestion in report["suggestions"])

    def test_handle_error_with_context(self):
        """测试带上下文处理错误"""
        error = ConfigurationError("Test error")
        context = "During configuration loading"

        report = self.error_handler.handle_error(error, context)

        assert report["context"] == context

    def test_log_error_called(self):
        """测试错误被记录到日志"""
        error = ConfigurationError("Test error")

        self.error_handler.handle_error(error)

        # 验证日志方法被调用
        self.mock_logger.print_error_details.assert_called_once()
        self.mock_logger.debug.assert_called_once()


class TestErrorUtilities:
    """测试错误工具函数"""

    def test_format_exception_details_basic(self):
        """测试基本异常格式化"""
        error = ValueError("Test error")

        details = format_exception_details(error)

        assert "错误类型: ValueError" in details
        assert "错误信息: Test error" in details

    def test_format_exception_details_with_details(self):
        """测试带详情的异常格式化"""
        error = ConfigurationError("Test error", "Additional details")

        details = format_exception_details(error)

        assert "详细信息: Additional details" in details

    def test_format_exception_details_with_status_code(self):
        """测试带状态码的异常格式化"""
        error = GitHubAPIError("API error", status_code=404)

        details = format_exception_details(error)

        assert "状态码: 404" in details

    def test_format_exception_details_with_traceback(self):
        """测试包含堆栈跟踪的异常格式化"""
        error = ValueError("Test error")

        details = format_exception_details(error, include_traceback=True)

        assert "堆栈跟踪:" in details

    @pytest.mark.skip(reason="需要模拟 get_logger 函数")
    def test_get_error_suggestions(self):
        """测试获取错误建议"""
        error = ConfigurationError("配置文件不存在")

        suggestions = get_error_suggestions(error)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0