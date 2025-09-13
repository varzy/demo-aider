"""测试 Aider 执行器"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from aider_automation.aider_executor import AiderExecutor
from aider_automation.models import Config, GitHubConfig, AiderConfig, AiderResult
from aider_automation.exceptions import AiderExecutionError


class TestAiderExecutor:
    """测试 Aider 执行器"""

    def setup_method(self):
        """设置测试方法"""
        self.temp_dir = tempfile.mkdtemp()
        github_config = GitHubConfig(token="test_token", repo="owner/repo")
        aider_config = AiderConfig(options=["--no-pretty"], model="gpt-4")
        self.config = Config(github=github_config, aider=aider_config)
        self.executor = AiderExecutor(self.config, self.temp_dir)

    def teardown_method(self):
        """清理测试方法"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_command_basic(self):
        """测试基本命令构建"""
        command = self.executor._build_command("test prompt")

        expected = ["aider", "--no-pretty", "--model", "gpt-4", "--yes", "--message", "test prompt"]
        assert command == expected

    def test_build_command_with_yes_option(self):
        """测试已包含 --yes 选项的命令构建"""
        aider_config = AiderConfig(options=["--no-pretty", "--yes"], model="gpt-4")
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"), aider=aider_config)
        executor = AiderExecutor(config)

        command = executor._build_command("test prompt")

        # 不应该重复添加 --yes
        yes_count = command.count("--yes")
        assert yes_count == 1

    def test_build_command_no_model(self):
        """测试没有模型配置的命令构建"""
        aider_config = AiderConfig(options=["--no-pretty"])
        config = Config(github=GitHubConfig(token="token", repo="owner/repo"), aider=aider_config)
        executor = AiderExecutor(config)

        command = executor._build_command("test prompt")

        expected = ["aider", "--no-pretty", "--yes", "--message", "test prompt"]
        assert command == expected

    @patch.object(AiderExecutor, '_run_aider_command')
    @patch.object(AiderExecutor, '_parse_output')
    def test_execute_success(self, mock_parse, mock_run):
        """测试成功执行"""
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        expected_aider_result = AiderResult(
            success=True,
            modified_files=["test.py"],
            summary="Test changes"
        )
        mock_parse.return_value = expected_aider_result

        result = self.executor.execute("test prompt")

        assert result == expected_aider_result
        mock_run.assert_called_once()
        mock_parse.assert_called_once_with(mock_result, "test prompt")

    def test_execute_empty_prompt(self):
        """测试空提示词"""
        with pytest.raises(AiderExecutionError) as exc_info:
            self.executor.execute("")

        assert "提示词不能为空" in str(exc_info.value)

    @patch('subprocess.run')
    def test_run_aider_command(self, mock_run):
        """测试运行 aider 命令"""
        mock_result = MagicMock(returncode=0, stdout="output", stderr="")
        mock_run.return_value = mock_result

        command = ["aider", "--message", "test"]
        result = self.executor._run_aider_command(command)

        assert result == mock_result
        # 检查调用参数，忽略路径的具体值
        args, kwargs = mock_run.call_args
        assert args[0] == command
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["timeout"] == 300
        assert str(kwargs["cwd"]).endswith(Path(self.temp_dir).name)

    def test_parse_output_success(self):
        """测试解析成功输出"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Modified: test.py\nCreated: new.py\nCompleted successfully"
        mock_result.stderr = ""

        result = self.executor._parse_output(mock_result, "test prompt")

        assert result.success is True
        assert "test.py" in result.modified_files
        assert "new.py" in result.modified_files
        assert result.error_message is None

    def test_parse_output_failure(self):
        """测试解析失败输出"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "Error occurred"
        mock_result.stderr = "Command failed"

        result = self.executor._parse_output(mock_result, "test prompt")

        assert result.success is False
        assert "Aider 执行失败" in result.error_message
        assert "Error occurredCommand failed" in result.output

    def test_extract_modified_files_various_patterns(self):
        """测试提取各种格式的修改文件"""
        output = """
        Modified: src/main.py
        Created: tests/test_new.py
        Edited: config.json
        ✓ utils.py
        Added: README.md
        """

        files = self.executor._extract_modified_files(output)

        expected_files = ["src/main.py", "tests/test_new.py", "config.json", "utils.py", "README.md"]
        for expected_file in expected_files:
            assert expected_file in files

    def test_extract_modified_files_chinese_patterns(self):
        """测试提取中文格式的修改文件"""
        output = """
        修改: src/main.py
        创建: tests/test_new.py
        编辑: config.json
        """

        files = self.executor._extract_modified_files(output)

        assert "src/main.py" in files
        assert "tests/test_new.py" in files
        assert "config.json" in files

    def test_extract_modified_files_no_matches(self):
        """测试没有匹配文件的情况"""
        output = "Some generic output without file modifications"

        files = self.executor._extract_modified_files(output)

        # 应该返回空列表或基于文件扩展名的推测
        assert isinstance(files, list)

    def test_extract_modified_files_limit(self):
        """测试文件数量限制"""
        # 创建超过 10 个文件的输出
        output = "\n".join([f"Modified: file{i}.py" for i in range(15)])

        files = self.executor._extract_modified_files(output)

        # 应该限制在 10 个文件以内
        assert len(files) <= 10

    def test_generate_summary_with_explicit_summary(self):
        """测试生成包含明确摘要的总结"""
        output = "Summary: Added user authentication feature\nModified: auth.py"
        prompt = "add auth"
        modified_files = ["auth.py"]

        summary = self.executor._generate_summary(output, prompt, modified_files)

        assert summary == "Added user authentication feature"

    def test_generate_summary_with_files(self):
        """测试基于文件生成摘要"""
        output = "Some output without explicit summary"
        prompt = "add feature"
        modified_files = ["file1.py", "file2.py"]

        summary = self.executor._generate_summary(output, prompt, modified_files)

        assert "2 个文件" in summary
        assert "file1.py" in summary
        assert "file2.py" in summary

    def test_generate_summary_no_files(self):
        """测试没有文件时生成摘要"""
        output = "Some output"
        prompt = "very long prompt that should be truncated because it exceeds fifty characters"
        modified_files = []

        summary = self.executor._generate_summary(output, prompt, modified_files)

        assert "执行了提示词" in summary
        assert "..." in summary  # 应该被截断

    @patch('subprocess.run')
    def test_validate_environment_success(self, mock_run):
        """测试环境验证成功"""
        mock_run.return_value = MagicMock(returncode=0, stdout="aider 0.1.0")

        # 不应该抛出异常
        self.executor.validate_environment()

        mock_run.assert_called_once_with(
            ["aider", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_validate_environment_aider_not_available(self, mock_run):
        """测试 aider 不可用"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Command not found")

        with pytest.raises(AiderExecutionError) as exc_info:
            self.executor.validate_environment()

        assert "Aider 工具不可用" in str(exc_info.value)

    @patch('subprocess.run')
    def test_validate_environment_timeout(self, mock_run):
        """测试环境验证超时"""
        mock_run.side_effect = subprocess.TimeoutExpired("aider", 10)

        with pytest.raises(AiderExecutionError) as exc_info:
            self.executor.validate_environment()

        assert "超时" in str(exc_info.value)

    @patch('subprocess.run')
    def test_validate_environment_not_found(self, mock_run):
        """测试 aider 命令未找到"""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(AiderExecutionError) as exc_info:
            self.executor.validate_environment()

        assert "找不到 aider 命令" in str(exc_info.value)

    @patch('subprocess.run')
    def test_get_aider_info_success(self, mock_run):
        """测试获取 aider 信息成功"""
        mock_run.return_value = MagicMock(returncode=0, stdout="aider 0.1.0")

        info = self.executor.get_aider_info()

        assert info["available"] is True
        assert "aider 0.1.0" in info["version"]
        assert info["command"] == ["aider", "--no-pretty"]

    @patch('subprocess.run')
    def test_get_aider_info_failure(self, mock_run):
        """测试获取 aider 信息失败"""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")

        info = self.executor.get_aider_info()

        assert info["available"] is False
        assert "Error" in info["error"]

    @patch('subprocess.run')
    def test_get_aider_info_exception(self, mock_run):
        """测试获取 aider 信息时发生异常"""
        mock_run.side_effect = Exception("Network error")

        info = self.executor.get_aider_info()

        assert info["available"] is False
        assert "Network error" in info["error"]