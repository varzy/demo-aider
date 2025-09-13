"""测试 GitHub 集成器"""

import json
import time
from unittest.mock import patch, MagicMock
import pytest
import requests

from aider_automation.github_integration import GitHubIntegrator
from aider_automation.models import Config, GitHubConfig, AiderResult, PRResult
from aider_automation.exceptions import GitHubAPIError


class TestGitHubIntegrator:
    """测试 GitHub 集成器"""

    def setup_method(self):
        """设置测试方法"""
        github_config = GitHubConfig(token="test_token", repo="owner/repo")
        self.config = Config(github=github_config)
        self.integrator = GitHubIntegrator(self.config)

    def test_init(self):
        """测试初始化"""
        assert self.integrator.config == self.config
        assert self.integrator.base_url == "https://api.github.com"
        assert "token test_token" in self.integrator.session.headers["Authorization"]
        assert "application/vnd.github.v3+json" in self.integrator.session.headers["Accept"]

    @patch('requests.Session.request')
    def test_create_pull_request_success(self, mock_request):
        """测试成功创建 PR"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "html_url": "https://github.com/owner/repo/pull/123",
            "number": 123
        }
        mock_request.return_value = mock_response

        result = self.integrator.create_pull_request(
            "feature-branch",
            "Test PR",
            "Test description"
        )

        assert result.success is True
        assert result.pr_url == "https://github.com/owner/repo/pull/123"
        assert result.pr_number == 123
        assert result.error_message is None

        # 验证请求参数
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert "repos/owner/repo/pulls" in args[1]
        assert kwargs["json"]["title"] == "Test PR"
        assert kwargs["json"]["body"] == "Test description"
        assert kwargs["json"]["head"] == "feature-branch"
        assert kwargs["json"]["base"] == "main"  # 默认分支

    @patch('requests.Session.request')
    def test_create_pull_request_with_custom_base(self, mock_request):
        """测试使用自定义基础分支创建 PR"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "html_url": "https://github.com/owner/repo/pull/123",
            "number": 123
        }
        mock_request.return_value = mock_response

        result = self.integrator.create_pull_request(
            "feature-branch",
            "Test PR",
            "Test description",
            "develop"
        )

        assert result.success is True

        # 验证基础分支
        args, kwargs = mock_request.call_args
        assert kwargs["json"]["base"] == "develop"

    @patch('requests.Session.request')
    def test_create_pull_request_failure(self, mock_request):
        """测试创建 PR 失败"""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "message": "Validation Failed",
            "errors": [{"message": "No commits between main and feature-branch"}]
        }
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_request.return_value = mock_response

        result = self.integrator.create_pull_request(
            "feature-branch",
            "Test PR",
            "Test description"
        )

        assert result.success is False
        assert "创建 PR 失败" in result.error_message
        assert "422" in result.error_message

    @patch('requests.Session.request')
    def test_create_pull_request_network_error(self, mock_request):
        """测试网络错误"""
        mock_request.side_effect = requests.RequestException("Network error")

        result = self.integrator.create_pull_request(
            "feature-branch",
            "Test PR",
            "Test description"
        )

        assert result.success is False
        assert "Network error" in result.error_message

    @patch('requests.Session.request')
    def test_get_repository_info_success(self, mock_request):
        """测试成功获取仓库信息"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "repo",
            "full_name": "owner/repo",
            "private": False
        }
        mock_request.return_value = mock_response

        info = self.integrator.get_repository_info()

        assert info["name"] == "repo"
        assert info["full_name"] == "owner/repo"
        assert info["private"] is False

    @patch('requests.Session.request')
    def test_get_repository_info_failure(self, mock_request):
        """测试获取仓库信息失败"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_response.text = json.dumps(mock_response.json.return_value)
        mock_request.return_value = mock_response

        with pytest.raises(GitHubAPIError) as exc_info:
            self.integrator.get_repository_info()

        assert "获取仓库信息失败" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @patch('requests.Session.request')
    def test_validate_access_success(self, mock_request):
        """测试验证访问权限成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.integrator.validate_access()

        assert result is True
        assert mock_request.call_count == 2  # 用户信息 + 仓库信息

    @patch('requests.Session.request')
    def test_validate_access_user_failure(self, mock_request):
        """测试用户访问失败"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        result = self.integrator.validate_access()

        assert result is False

    @patch('requests.Session.request')
    def test_validate_access_repo_failure(self, mock_request):
        """测试仓库访问失败"""
        # 第一次调用（用户信息）成功，第二次调用（仓库信息）失败
        mock_request.side_effect = [
            MagicMock(status_code=200),  # 用户信息成功
            MagicMock(status_code=404)   # 仓库信息失败
        ]

        result = self.integrator.validate_access()

        assert result is False

    @patch('requests.Session.request')
    def test_check_branch_exists_true(self, mock_request):
        """测试分支存在"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.integrator.check_branch_exists("feature-branch")

        assert result is True

        # 验证请求 URL
        args, kwargs = mock_request.call_args
        assert "branches/feature-branch" in args[1]

    @patch('requests.Session.request')
    def test_check_branch_exists_false(self, mock_request):
        """测试分支不存在"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.integrator.check_branch_exists("nonexistent-branch")

        assert result is False

    def test_format_pr_body(self):
        """测试格式化 PR 描述"""
        aider_result = AiderResult(
            success=True,
            modified_files=["file1.py", "file2.py"],
            summary="Added new features"
        )

        body = self.integrator.format_pr_body(aider_result, "Add user authentication")

        assert "Add user authentication" in body
        assert "file1.py" in body
        assert "file2.py" in body
        assert "Added new features" in body

    def test_format_pr_body_no_files(self):
        """测试没有修改文件的 PR 描述"""
        aider_result = AiderResult(
            success=True,
            modified_files=[],
            summary="No file changes"
        )

        body = self.integrator.format_pr_body(aider_result, "Test prompt")

        assert "Test prompt" in body
        assert "无文件修改记录" in body

    def test_format_pr_title(self):
        """测试格式化 PR 标题"""
        aider_result = AiderResult(
            success=True,
            summary="Added authentication"
        )

        title = self.integrator.format_pr_title(aider_result, "Add auth feature")

        assert "Added authentication" in title

    def test_format_pr_title_long_summary(self):
        """测试长摘要的 PR 标题"""
        long_summary = "This is a very long summary that exceeds fifty characters and should be truncated"
        aider_result = AiderResult(
            success=True,
            summary=long_summary
        )

        title = self.integrator.format_pr_title(aider_result, "Test")

        assert len(title) <= 100
        assert "..." in title

    def test_format_pr_title_no_summary(self):
        """测试没有摘要的 PR 标题"""
        aider_result = AiderResult(
            success=True,
            summary=""
        )

        title = self.integrator.format_pr_title(aider_result, "Test prompt")

        assert "Test prompt" in title

    def test_parse_repo_info_valid(self):
        """测试解析有效仓库信息"""
        owner, repo = self.integrator._parse_repo_info()

        assert owner == "owner"
        assert repo == "repo"

    def test_parse_repo_info_invalid_format(self):
        """测试解析无效仓库格式"""
        # 由于 GitHubConfig 会在创建时验证格式，这里测试 Pydantic 验证
        with pytest.raises(ValueError) as exc_info:
            GitHubConfig(token="token", repo="invalid_repo")

        assert "GitHub 仓库格式必须为 owner/repo" in str(exc_info.value)

    def test_parse_repo_info_empty_parts(self):
        """测试解析空的仓库部分"""
        # 由于 GitHubConfig 会在创建时验证格式，这里测试 Pydantic 验证
        with pytest.raises(ValueError) as exc_info:
            GitHubConfig(token="token", repo="/repo")

        assert "owner 和 repo 名称不能为空" in str(exc_info.value)

    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """测试成功的请求"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        response = self.integrator._make_request("GET", "https://api.github.com/test")

        assert response == mock_response
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_make_request_rate_limit(self, mock_sleep, mock_request):
        """测试速率限制处理"""
        # 第一次请求返回 429，第二次请求成功
        rate_limit_response = MagicMock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {'X-RateLimit-Reset': str(int(time.time()) + 60)}

        success_response = MagicMock()
        success_response.status_code = 200

        mock_request.side_effect = [rate_limit_response, success_response]

        response = self.integrator._make_request("GET", "https://api.github.com/test")

        assert response == success_response
        assert mock_request.call_count == 2
        mock_sleep.assert_called_once()

    @patch('requests.Session.request')
    def test_make_request_max_retries_exceeded(self, mock_request):
        """测试超过最大重试次数"""
        mock_request.side_effect = requests.RequestException("Network error")

        with pytest.raises(GitHubAPIError) as exc_info:
            self.integrator._make_request("GET", "https://api.github.com/test", max_retries=1)

        assert "GitHub API 请求失败" in str(exc_info.value)
        assert mock_request.call_count == 2  # 原始请求 + 1 次重试

    def test_extract_error_message_standard_format(self):
        """测试提取标准格式错误信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": "Validation Failed",
            "errors": [
                {"message": "Error 1"},
                {"message": "Error 2"}
            ]
        }

        error_msg = self.integrator._extract_error_message(mock_response)

        assert "Validation Failed" in error_msg
        assert "Error 1" in error_msg
        assert "Error 2" in error_msg

    def test_extract_error_message_simple_format(self):
        """测试提取简单格式错误信息"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": "Not Found"}

        error_msg = self.integrator._extract_error_message(mock_response)

        assert error_msg == "Not Found"

    def test_extract_error_message_json_parse_error(self):
        """测试 JSON 解析错误"""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Raw error text"

        error_msg = self.integrator._extract_error_message(mock_response)

        assert error_msg == "Raw error text"