"""测试 Git 管理器"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from aider_automation.git_manager import GitManager
from aider_automation.exceptions import GitOperationError


class TestGitManager:
    """测试 Git 管理器"""

    def setup_method(self):
        """设置测试方法"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_manager = GitManager(self.temp_dir)

    def teardown_method(self):
        """清理测试方法"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.object(GitManager, '_run_git_command')
    @patch.object(GitManager, '_branch_exists')
    def test_create_branch_success(self, mock_branch_exists, mock_run_git):
        """测试成功创建分支"""
        mock_branch_exists.return_value = False
        mock_run_git.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.git_manager.create_branch("feature-test")

        assert result is True
        mock_branch_exists.assert_called_once_with("feature-test")
        mock_run_git.assert_called_once_with(["checkout", "-b", "feature-test"])

    @patch.object(GitManager, '_branch_exists')
    def test_create_branch_already_exists(self, mock_branch_exists):
        """测试创建已存在的分支"""
        mock_branch_exists.return_value = True

        with pytest.raises(GitOperationError) as exc_info:
            self.git_manager.create_branch("existing-branch")

        assert "已存在" in str(exc_info.value)

    @patch.object(GitManager, '_run_git_command')
    @patch.object(GitManager, '_branch_exists')
    def test_create_branch_git_error(self, mock_branch_exists, mock_run_git):
        """测试 Git 命令执行失败"""
        mock_branch_exists.return_value = False
        mock_run_git.return_value = MagicMock(returncode=1, stderr="Git error")

        with pytest.raises(GitOperationError) as exc_info:
            self.git_manager.create_branch("invalid-branch")

        assert "创建分支失败" in str(exc_info.value)

    @patch.object(GitManager, '_run_git_command')
    @patch.object(GitManager, '_branch_exists')
    def test_switch_branch_success(self, mock_branch_exists, mock_run_git):
        """测试成功切换分支"""
        mock_branch_exists.return_value = True
        mock_run_git.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.git_manager.switch_branch("existing-branch")

        assert result is True
        mock_run_git.assert_called_once_with(["checkout", "existing-branch"])

    @patch.object(GitManager, '_branch_exists')
    def test_switch_branch_not_exists(self, mock_branch_exists):
        """测试切换到不存在的分支"""
        mock_branch_exists.return_value = False

        with pytest.raises(GitOperationError) as exc_info:
            self.git_manager.switch_branch("nonexistent-branch")

        assert "不存在" in str(exc_info.value)

    @patch.object(GitManager, '_run_git_command')
    def test_has_changes_true(self, mock_run_git):
        """测试有未提交更改"""
        mock_run_git.return_value = MagicMock(
            returncode=0,
            stdout=" M file1.py\n?? file2.py\n"
        )

        result = self.git_manager.has_changes()

        assert result is True
        mock_run_git.assert_called_once_with(["status", "--porcelain"])

    @patch.object(GitManager, '_run_git_command')
    def test_has_changes_false(self, mock_run_git):
        """测试没有未提交更改"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="")

        result = self.git_manager.has_changes()

        assert result is False

    @patch.object(GitManager, '_run_git_command')
    def test_get_changed_files(self, mock_run_git):
        """测试获取更改文件列表"""
        mock_run_git.return_value = MagicMock(
            returncode=0,
            stdout=" M file1.py\n?? file2.py\nA  file3.py\n"
        )

        files = self.git_manager.get_changed_files()

        assert files == ["file1.py", "file2.py", "file3.py"]

    @patch.object(GitManager, '_run_git_command')
    def test_add_all_changes_success(self, mock_run_git):
        """测试成功添加所有更改"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.git_manager.add_all_changes()

        assert result is True
        mock_run_git.assert_called_once_with(["add", "."])

    @patch.object(GitManager, '_run_git_command')
    def test_commit_changes_success(self, mock_run_git):
        """测试成功提交更改"""
        # 模拟提交命令和获取哈希命令
        mock_run_git.side_effect = [
            MagicMock(returncode=0, stdout="", stderr=""),  # commit
            MagicMock(returncode=0, stdout="abc123def456", stderr="")  # rev-parse
        ]

        commit_hash = self.git_manager.commit_changes("Test commit message")

        assert commit_hash == "abc123def456"
        assert mock_run_git.call_count == 2

    def test_commit_changes_empty_message(self):
        """测试空提交信息"""
        with pytest.raises(GitOperationError) as exc_info:
            self.git_manager.commit_changes("")

        assert "提交信息不能为空" in str(exc_info.value)

    @patch.object(GitManager, '_run_git_command')
    def test_push_branch_success(self, mock_run_git):
        """测试成功推送分支"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.git_manager.push_branch("feature-branch")

        assert result is True
        mock_run_git.assert_called_once_with(["push", "-u", "origin", "feature-branch"])

    @patch.object(GitManager, '_run_git_command')
    def test_get_current_branch(self, mock_run_git):
        """测试获取当前分支"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="main")

        branch = self.git_manager.get_current_branch()

        assert branch == "main"
        mock_run_git.assert_called_once_with(["branch", "--show-current"])

    @patch.object(GitManager, '_run_git_command')
    def test_get_remote_url(self, mock_run_git):
        """测试获取远程仓库 URL"""
        mock_run_git.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/owner/repo.git"
        )

        url = self.git_manager.get_remote_url()

        assert url == "https://github.com/owner/repo.git"
        mock_run_git.assert_called_once_with(["remote", "get-url", "origin"])

    @patch.object(GitManager, 'get_remote_url')
    def test_get_repo_info_https(self, mock_get_remote_url):
        """测试解析 HTTPS 仓库信息"""
        mock_get_remote_url.return_value = "https://github.com/owner/repo.git"

        owner, repo = self.git_manager.get_repo_info()

        assert owner == "owner"
        assert repo == "repo"

    @patch.object(GitManager, 'get_remote_url')
    def test_get_repo_info_ssh(self, mock_get_remote_url):
        """测试解析 SSH 仓库信息"""
        mock_get_remote_url.return_value = "git@github.com:owner/repo.git"

        owner, repo = self.git_manager.get_repo_info()

        assert owner == "owner"
        assert repo == "repo"

    @patch.object(GitManager, 'get_remote_url')
    def test_get_repo_info_invalid_url(self, mock_get_remote_url):
        """测试无效的仓库 URL"""
        mock_get_remote_url.return_value = "https://gitlab.com/owner/repo.git"

        with pytest.raises(GitOperationError) as exc_info:
            self.git_manager.get_repo_info()

        assert "不支持的远程 URL 格式" in str(exc_info.value)

    @patch.object(GitManager, '_run_git_command')
    def test_branch_exists_true(self, mock_run_git):
        """测试分支存在"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="  feature-branch")

        result = self.git_manager._branch_exists("feature-branch")

        assert result is True

    @patch.object(GitManager, '_run_git_command')
    def test_branch_exists_false(self, mock_run_git):
        """测试分支不存在"""
        mock_run_git.return_value = MagicMock(returncode=0, stdout="")

        result = self.git_manager._branch_exists("nonexistent-branch")

        assert result is False

    def test_run_git_command(self):
        """测试运行 Git 命令"""
        # 这个测试需要真实的 Git 环境，所以我们只测试命令构造
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            self.git_manager._run_git_command(["status"])

            # 检查调用参数，忽略路径的具体值（因为 resolve() 可能改变路径格式）
            args, kwargs = mock_run.call_args
            assert args[0] == ["git", "status"]
            assert kwargs["capture_output"] is True
            assert kwargs["text"] is True
            assert kwargs["timeout"] == 30
            assert str(kwargs["cwd"]).endswith(Path(self.temp_dir).name)