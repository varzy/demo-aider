"""测试依赖项检查器"""

import subprocess
from unittest.mock import patch, MagicMock
import pytest
import requests

from aider_automation.dependencies import DependencyChecker
from aider_automation.models import Config, GitHubConfig
from aider_automation.exceptions import DependencyError


class TestDependencyChecker:
    """测试依赖项检查器"""

    def setup_method(self):
        """设置测试方法"""
        self.checker = DependencyChecker()

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_aider_success(self, mock_run, mock_which):
        """测试 aider 检查成功"""
        mock_which.return_value = "/usr/local/bin/aider"
        mock_run.return_value = MagicMock(returncode=0, stdout="aider 0.1.0")

        result = self.checker.check_aider()

        assert result is True
        mock_which.assert_called_once_with("aider")
        mock_run.assert_called_once_with(
            ["aider", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('shutil.which')
    def test_check_aider_not_found(self, mock_which):
        """测试 aider 未找到"""
        mock_which.return_value = None

        result = self.checker.check_aider()

        assert result is False

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_aider_command_failed(self, mock_run, mock_which):
        """测试 aider 命令执行失败"""
        mock_which.return_value = "/usr/local/bin/aider"
        mock_run.return_value = MagicMock(returncode=1)

        result = self.checker.check_aider()

        assert result is False

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_aider_timeout(self, mock_run, mock_which):
        """测试 aider 命令超时"""
        mock_which.return_value = "/usr/local/bin/aider"
        mock_run.side_effect = subprocess.TimeoutExpired("aider", 10)

        result = self.checker.check_aider()

        assert result is False

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_git_success(self, mock_run, mock_which):
        """测试 Git 检查成功"""
        mock_which.return_value = "/usr/bin/git"
        mock_run.return_value = MagicMock(returncode=0, stdout="git version 2.39.0")

        result = self.checker.check_git()

        assert result is True
        mock_which.assert_called_once_with("git")
        mock_run.assert_called_once_with(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('shutil.which')
    def test_check_git_not_found(self, mock_which):
        """测试 Git 未找到"""
        mock_which.return_value = None

        result = self.checker.check_git()

        assert result is False

    @patch('requests.get')
    def test_check_github_access_success(self, mock_get):
        """测试 GitHub 访问成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.checker.check_github_access("valid_token")

        assert result is True
        mock_get.assert_called_once_with(
            "https://api.github.com/user",
            headers={
                "Authorization": "token valid_token",
                "Accept": "application/vnd.github.v3+json"
            },
            timeout=10
        )

    @patch('requests.get')
    def test_check_github_access_unauthorized(self, mock_get):
        """测试 GitHub 访问未授权"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = self.checker.check_github_access("invalid_token")

        assert result is False

    @patch('requests.get')
    def test_check_github_access_network_error(self, mock_get):
        """测试 GitHub 访问网络错误"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = self.checker.check_github_access("token")

        assert result is False

    @patch('subprocess.run')
    def test_check_git_repository_success(self, mock_run):
        """测试 Git 仓库检查成功"""
        mock_run.return_value = MagicMock(returncode=0, stdout=".git")

        result = self.checker.check_git_repository()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=5
        )

    @patch('subprocess.run')
    def test_check_git_repository_not_repo(self, mock_run):
        """测试不是 Git 仓库"""
        mock_run.return_value = MagicMock(returncode=128)

        result = self.checker.check_git_repository()

        assert result is False

    @patch('subprocess.run')
    def test_check_git_remote_success(self, mock_run):
        """测试 Git 远程仓库检查成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="origin\thttps://github.com/user/repo.git (fetch)\n"
        )

        result = self.checker.check_git_remote()

        assert result is True

    @patch('subprocess.run')
    def test_check_git_remote_no_remote(self, mock_run):
        """测试没有远程仓库"""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        result = self.checker.check_git_remote()

        assert result is False

    def test_check_all_dependencies_all_good(self):
        """测试所有依赖项都正常"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_aider', return_value=True), \
             patch.object(self.checker, 'check_git', return_value=True), \
             patch.object(self.checker, 'check_git_repository', return_value=True), \
             patch.object(self.checker, 'check_git_remote', return_value=True), \
             patch.object(self.checker, 'check_github_access', return_value=True):

            missing_deps = self.checker.check_all_dependencies(config)

            assert missing_deps == []

    def test_check_all_dependencies_missing_aider(self):
        """测试缺少 aider"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_aider', return_value=False), \
             patch.object(self.checker, 'check_git', return_value=True), \
             patch.object(self.checker, 'check_git_repository', return_value=True), \
             patch.object(self.checker, 'check_git_remote', return_value=True), \
             patch.object(self.checker, 'check_github_access', return_value=True):

            missing_deps = self.checker.check_all_dependencies(config)

            assert len(missing_deps) == 1
            assert "aider" in missing_deps[0]

    def test_check_all_dependencies_missing_git(self):
        """测试缺少 Git"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_aider', return_value=True), \
             patch.object(self.checker, 'check_git', return_value=False), \
             patch.object(self.checker, 'check_github_access', return_value=True):

            missing_deps = self.checker.check_all_dependencies(config)

            assert len(missing_deps) == 1
            assert "git" in missing_deps[0]

    def test_check_all_dependencies_not_git_repo(self):
        """测试不是 Git 仓库"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_aider', return_value=True), \
             patch.object(self.checker, 'check_git', return_value=True), \
             patch.object(self.checker, 'check_git_repository', return_value=False), \
             patch.object(self.checker, 'check_github_access', return_value=True):

            missing_deps = self.checker.check_all_dependencies(config)

            assert len(missing_deps) == 1
            assert "git-repo" in missing_deps[0]

    def test_check_all_dependencies_github_access_failed(self):
        """测试 GitHub 访问失败"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_aider', return_value=True), \
             patch.object(self.checker, 'check_git', return_value=True), \
             patch.object(self.checker, 'check_git_repository', return_value=True), \
             patch.object(self.checker, 'check_git_remote', return_value=True), \
             patch.object(self.checker, 'check_github_access', return_value=False):

            missing_deps = self.checker.check_all_dependencies(config)

            assert len(missing_deps) == 1
            assert "github-access" in missing_deps[0]

    def test_get_dependency_info(self):
        """测试获取依赖项信息"""
        with patch.object(self.checker, 'check_aider', return_value=True), \
             patch.object(self.checker, 'check_git', return_value=True), \
             patch.object(self.checker, 'check_git_repository', return_value=True), \
             patch.object(self.checker, 'check_git_remote', return_value=True), \
             patch('subprocess.run') as mock_run:

            # 模拟 aider --version 输出
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="aider 0.1.0"),  # aider version
                MagicMock(returncode=0, stdout="git version 2.39.0")  # git version
            ]

            info = self.checker.get_dependency_info()

            assert info["aider"]["available"] is True
            assert "aider 0.1.0" in info["aider"]["version"]
            assert info["git"]["available"] is True
            assert "git version 2.39.0" in info["git"]["version"]
            assert info["git"]["repository"] is True
            assert info["git"]["remote"] is True

    def test_validate_environment_success(self):
        """测试环境验证成功"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        with patch.object(self.checker, 'check_all_dependencies', return_value=[]):
            # 不应该抛出异常
            self.checker.validate_environment(config)

    def test_validate_environment_failure(self):
        """测试环境验证失败"""
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"))

        missing_deps = ["aider - AI 编程助手工具未安装或不可用"]

        with patch.object(self.checker, 'check_all_dependencies', return_value=missing_deps):
            with pytest.raises(DependencyError) as exc_info:
                self.checker.validate_environment(config)

            assert "aider" in str(exc_info.value)
            assert "pip install aider-chat" in exc_info.value.details