"""测试核心数据模型"""

import pytest
from datetime import datetime, timedelta
from aider_automation.models import (
    Config, GitHubConfig, AiderConfig, GitConfig, TemplateConfig,
    AiderResult, PRResult, WorkflowState
)


class TestGitHubConfig:
    """测试 GitHub 配置模型"""

    def test_valid_github_config(self):
        """测试有效的 GitHub 配置"""
        config = GitHubConfig(token="test_token", repo="owner/repo")
        assert config.token == "test_token"
        assert config.repo == "owner/repo"

    def test_invalid_repo_format(self):
        """测试无效的仓库格式"""
        with pytest.raises(ValueError) as exc_info:
            GitHubConfig(token="test_token", repo="invalid_repo")

        assert "GitHub 仓库格式必须为 owner/repo" in str(exc_info.value)

    def test_empty_owner_or_repo(self):
        """测试空的 owner 或 repo"""
        with pytest.raises(ValueError) as exc_info:
            GitHubConfig(token="test_token", repo="/repo")

        assert "owner 和 repo 名称不能为空" in str(exc_info.value)


class TestGitConfig:
    """测试 Git 配置模型"""

    def test_branch_prefix_auto_slash(self):
        """测试分支前缀自动添加斜杠"""
        config = GitConfig(branch_prefix="feature")
        assert config.branch_prefix == "feature/"

    def test_branch_prefix_existing_slash(self):
        """测试已有斜杠的分支前缀"""
        config = GitConfig(branch_prefix="feature/")
        assert config.branch_prefix == "feature/"

    def test_empty_branch_prefix(self):
        """测试空分支前缀"""
        config = GitConfig(branch_prefix="")
        assert config.branch_prefix == ""


class TestConfig:
    """测试主配置模型"""

    def test_config_creation_with_required_fields(self):
        """测试使用必需字段创建配置"""
        github_config = GitHubConfig(token="test_token", repo="owner/repo")
        config = Config(github=github_config)

        assert config.github_token == "test_token"
        assert config.github_repo == "owner/repo"
        assert config.default_branch == "main"
        assert config.git.branch_prefix == "aider-automation/"

    def test_config_with_all_fields(self):
        """测试使用所有字段创建配置"""
        github_config = GitHubConfig(token="test_token", repo="owner/repo")
        aider_config = AiderConfig(options=["--no-pretty", "--yes"], model="gpt-4")
        git_config = GitConfig(default_branch="develop", branch_prefix="feature/")
        template_config = TemplateConfig(
            commit_message="chore: {summary}",
            pr_title="Auto: {summary}",
            pr_body="Changes: {prompt}"
        )

        config = Config(
            github=github_config,
            aider=aider_config,
            git=git_config,
            templates=template_config
        )

        assert config.aider_options == ["--no-pretty", "--yes"]
        assert config.aider.model == "gpt-4"
        assert config.default_branch == "develop"
        assert config.commit_message_template == "chore: {summary}"
        assert config.pr_title_template == "Auto: {summary}"
        assert config.pr_body_template == "Changes: {prompt}"

    def test_config_backward_compatibility_properties(self):
        """测试配置的向后兼容属性"""
        github_config = GitHubConfig(token="test_token", repo="owner/repo")
        aider_config = AiderConfig(options=["--verbose"], model="gpt-3.5-turbo")
        git_config = GitConfig(default_branch="master", branch_prefix="hotfix/")
        template_config = TemplateConfig(
            commit_message="fix: {summary}",
            pr_title="Hotfix: {summary}",
            pr_body="Urgent fix: {prompt}"
        )

        config = Config(
            github=github_config,
            aider=aider_config,
            git=git_config,
            templates=template_config
        )

        # 测试所有向后兼容的属性
        assert config.github_token == "test_token"
        assert config.github_repo == "owner/repo"
        assert config.aider_options == ["--verbose"]
        assert config.default_branch == "master"
        assert config.commit_message_template == "fix: {summary}"
        assert config.pr_title_template == "Hotfix: {summary}"
        assert config.pr_body_template == "Urgent fix: {prompt}"


class TestAiderResult:
    """测试 AiderResult 数据类"""

    def test_aider_result_success(self):
        """测试成功的 Aider 结果"""
        result = AiderResult(
            success=True,
            modified_files=["file1.py", "file2.py"],
            summary="Added new features",
            output="Aider output here"
        )
        assert result.success is True
        assert len(result.modified_files) == 2
        assert result.summary == "Added new features"
        assert result.error_message is None

    def test_aider_result_failure(self):
        """测试失败的 Aider 结果"""
        result = AiderResult(
            success=False,
            error_message="Aider execution failed"
        )
        assert result.success is False
        assert result.error_message == "Aider execution failed"
        assert len(result.modified_files) == 0


class TestPRResult:
    """测试 PRResult 数据类"""

    def test_pr_result_success(self):
        """测试成功的 PR 结果"""
        result = PRResult(
            success=True,
            pr_url="https://github.com/owner/repo/pull/123",
            pr_number=123
        )
        assert result.success is True
        assert result.pr_url == "https://github.com/owner/repo/pull/123"
        assert result.pr_number == 123
        assert result.error_message is None

    def test_pr_result_failure(self):
        """测试失败的 PR 结果"""
        result = PRResult(
            success=False,
            error_message="Failed to create PR"
        )
        assert result.success is False
        assert result.error_message == "Failed to create PR"
        assert result.pr_url is None
        assert result.pr_number is None


class TestWorkflowState:
    """测试 WorkflowState 数据类"""

    def test_workflow_state_creation(self):
        """测试工作流程状态创建"""
        github_config = GitHubConfig(token="token", repo="owner/repo")
        config = Config(github=github_config)
        state = WorkflowState(
            prompt="Test prompt",
            branch_name="test-branch",
            config=config
        )
        assert state.prompt == "Test prompt"
        assert state.branch_name == "test-branch"
        assert isinstance(state.start_time, datetime)
        assert state.duration is None

    def test_workflow_state_duration(self):
        """测试工作流程时长计算"""
        github_config = GitHubConfig(token="token", repo="owner/repo")
        config = Config(github=github_config)
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)

        state = WorkflowState(
            prompt="Test prompt",
            branch_name="test-branch",
            config=config,
            start_time=start_time,
            end_time=end_time
        )
        assert state.duration == 30.0

    def test_workflow_state_with_results(self):
        """测试包含结果的工作流程状态"""
        github_config = GitHubConfig(token="token", repo="owner/repo")
        config = Config(github=github_config)

        aider_result = AiderResult(
            success=True,
            modified_files=["test.py"],
            summary="Test changes"
        )

        pr_result = PRResult(
            success=True,
            pr_url="https://github.com/owner/repo/pull/1",
            pr_number=1
        )

        state = WorkflowState(
            prompt="Test prompt",
            branch_name="test-branch",
            config=config,
            aider_result=aider_result,
            commit_hash="abc123",
            pr_result=pr_result
        )

        assert state.aider_result.success is True
        assert state.commit_hash == "abc123"
        assert state.pr_result.pr_number == 1