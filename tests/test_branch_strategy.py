"""测试分支策略"""

from unittest.mock import patch, MagicMock
import pytest

from aider_automation.branch_strategy import BranchStrategy
from aider_automation.git_manager import GitManager
from aider_automation.exceptions import GitOperationError


class TestBranchStrategy:
    """测试分支策略"""

    def setup_method(self):
        """设置测试方法"""
        self.mock_git_manager = MagicMock(spec=GitManager)
        self.branch_strategy = BranchStrategy(self.mock_git_manager, "test-prefix/")

    def test_generate_branch_name_with_base_name(self):
        """测试使用基础名称生成分支名"""
        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.generate_branch_name(
                "some prompt",
                "custom-feature"
            )

            assert branch_name.startswith("test-prefix/custom-feature-20240101-120000")

    def test_generate_branch_name_from_prompt(self):
        """测试从提示词生成分支名"""
        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.generate_branch_name(
                "add user authentication feature"
            )

            assert "test-prefix/" in branch_name
            assert "add-user-authentication-feature" in branch_name
            assert "20240101-120000" in branch_name

    def test_generate_branch_name_chinese_prompt(self):
        """测试中文提示词生成分支名"""
        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.generate_branch_name(
                "添加用户认证功能"
            )

            assert "test-prefix/" in branch_name
            assert "20240101-120000" in branch_name

    def test_generate_branch_name_long_prompt(self):
        """测试长提示词生成分支名"""
        long_prompt = "add a very long feature that does many things " * 10

        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.generate_branch_name(long_prompt)

            # 确保分支名称不会太长
            assert len(branch_name) <= 250

    def test_create_unique_branch_success(self):
        """测试成功创建唯一分支"""
        self.mock_git_manager._branch_exists.return_value = False
        self.mock_git_manager.create_branch.return_value = True

        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.create_unique_branch(
                "test feature",
                "test-branch"
            )

            assert "test-prefix/test-branch-20240101-120000" in branch_name
            self.mock_git_manager.create_branch.assert_called_once()

    def test_create_unique_branch_with_conflict(self):
        """测试创建分支时有冲突"""
        # 第一次检查分支存在，第二次不存在
        self.mock_git_manager._branch_exists.side_effect = [True, False]
        self.mock_git_manager.create_branch.return_value = True

        with patch('aider_automation.branch_strategy.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"

            branch_name = self.branch_strategy.create_unique_branch(
                "test feature",
                "test-branch"
            )

            # 应该在原名称后添加 -1
            assert branch_name.endswith("-1")
            self.mock_git_manager.create_branch.assert_called_once()

    def test_create_unique_branch_too_many_conflicts(self):
        """测试分支冲突过多"""
        self.mock_git_manager._branch_exists.return_value = True

        with pytest.raises(GitOperationError) as exc_info:
            self.branch_strategy.create_unique_branch("test feature", "test-branch")

        assert "无法生成唯一分支名称" in str(exc_info.value)

    def test_handle_branch_conflict_not_exists(self):
        """测试处理不存在的分支冲突"""
        self.mock_git_manager._branch_exists.return_value = False
        self.mock_git_manager.create_branch.return_value = True

        result = self.branch_strategy.handle_branch_conflict("new-branch", "test prompt")

        assert result == "new-branch"
        self.mock_git_manager.create_branch.assert_called_once_with("new-branch")

    def test_handle_branch_conflict_current_branch(self):
        """测试处理当前分支冲突"""
        self.mock_git_manager._branch_exists.return_value = True
        self.mock_git_manager.get_current_branch.return_value = "existing-branch"

        result = self.branch_strategy.handle_branch_conflict("existing-branch", "test prompt")

        assert result == "existing-branch"

    def test_handle_branch_conflict_switch_success(self):
        """测试成功切换到现有分支"""
        self.mock_git_manager._branch_exists.return_value = True
        self.mock_git_manager.get_current_branch.return_value = "current-branch"
        self.mock_git_manager.has_changes.return_value = False
        self.mock_git_manager.switch_branch.return_value = True

        result = self.branch_strategy.handle_branch_conflict("existing-branch", "test prompt")

        assert result == "existing-branch"
        self.mock_git_manager.switch_branch.assert_called_once_with("existing-branch")

    def test_handle_branch_conflict_has_changes(self):
        """测试有未提交更改时的分支冲突"""
        self.mock_git_manager._branch_exists.return_value = True
        self.mock_git_manager.get_current_branch.return_value = "current-branch"
        self.mock_git_manager.has_changes.return_value = True

        with pytest.raises(GitOperationError) as exc_info:
            self.branch_strategy.handle_branch_conflict("existing-branch", "test prompt")

        assert "未提交的更改" in str(exc_info.value)

    def test_generate_name_from_prompt_english(self):
        """测试从英文提示词生成名称"""
        name = self.branch_strategy._generate_name_from_prompt(
            "add user authentication and authorization feature"
        )

        assert "add" in name
        assert "user" in name
        assert "authentication" in name
        # 停用词应该被过滤
        assert "and" not in name

    def test_generate_name_from_prompt_mixed(self):
        """测试从混合语言提示词生成名称"""
        name = self.branch_strategy._generate_name_from_prompt(
            "添加 user authentication 功能"
        )

        # 应该包含有意义的词
        assert "user" in name
        assert "authentication" in name

    def test_generate_name_from_prompt_no_meaningful_words(self):
        """测试没有有意义词的提示词"""
        name = self.branch_strategy._generate_name_from_prompt("a the is")

        assert name == "feature"

    def test_sanitize_branch_name_special_chars(self):
        """测试清理特殊字符"""
        name = self.branch_strategy._sanitize_branch_name("test@#$%^&*()feature")

        assert name == "test-feature"

    def test_sanitize_branch_name_spaces(self):
        """测试清理空格"""
        name = self.branch_strategy._sanitize_branch_name("test feature name")

        assert name == "test-feature-name"

    def test_sanitize_branch_name_consecutive_dashes(self):
        """测试清理连续连字符"""
        name = self.branch_strategy._sanitize_branch_name("test---feature")

        assert name == "test-feature"

    def test_sanitize_branch_name_dots(self):
        """测试清理点号"""
        name = self.branch_strategy._sanitize_branch_name(".test.feature.")

        # 点号会被替换为连字符，开头和结尾的点号会被移除
        assert name == "test-feature"

    def test_sanitize_branch_name_empty(self):
        """测试清理空名称"""
        name = self.branch_strategy._sanitize_branch_name("@#$%")

        assert name == "feature"

    def test_sanitize_branch_name_starts_with_dot(self):
        """测试以点开头的名称"""
        name = self.branch_strategy._sanitize_branch_name(".hidden-feature")

        # 开头的点号被移除，不会添加 branch- 前缀
        assert name == "hidden-feature"