"""测试日志管理器"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from aider_automation.logger import Logger, WorkflowLogger, get_logger, get_workflow_logger


class TestLogger:
    """测试日志管理器"""

    def test_logger_init_default(self):
        """测试默认初始化"""
        logger = Logger()

        assert logger.name == "aider-automation"
        assert logger.verbose is False
        assert logger.console is not None
        assert logger.logger is not None

    def test_logger_init_with_params(self):
        """测试带参数初始化"""
        logger = Logger(
            name="test-logger",
            level="DEBUG",
            verbose=True
        )

        assert logger.name == "test-logger"
        assert logger.verbose is True

    def test_logger_with_file(self):
        """测试文件日志"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = Logger(log_file=str(log_file))
            logger.info("Test message")

            assert log_file.exists()
            content = log_file.read_text(encoding='utf-8')
            assert "Test message" in content

    def test_logging_methods(self):
        """测试日志记录方法"""
        with patch.object(Logger, '_setup_console_handler'):
            logger = Logger()
            logger.logger = MagicMock()

            logger.info("Info message")
            logger.debug("Debug message")
            logger.warning("Warning message")
            logger.error("Error message")

            logger.logger.info.assert_called_with("Info message")
            logger.logger.debug.assert_called_with("Debug message")
            logger.logger.warning.assert_called_with("Warning message")
            logger.logger.error.assert_called_with("Error message")

    def test_console_methods(self):
        """测试控制台输出方法"""
        logger = Logger()
        logger.console = MagicMock()

        logger.success("Success message")
        logger.step("Step message")
        logger.progress("Progress message")
        logger.section("Section title")

        # 验证 console.print 被调用
        assert logger.console.print.call_count >= 4

    def test_print_summary(self):
        """测试打印摘要"""
        logger = Logger()
        logger.console = MagicMock()

        items = ["Item 1", "Item 2", "Item 3"]
        logger.print_summary("Test Summary", items)

        # 验证调用次数（标题 + 每个项目）
        assert logger.console.print.call_count >= len(items) + 1

    def test_print_error_details(self):
        """测试打印错误详情"""
        logger = Logger()
        logger.console = MagicMock()

        error = Exception("Test error")
        error.details = "Additional details"
        suggestions = ["Suggestion 1", "Suggestion 2"]

        logger.print_error_details(error, suggestions)

        # 验证调用了多次 print
        assert logger.console.print.call_count >= 3

    def test_create_progress_bar(self):
        """测试创建进度条"""
        logger = Logger()

        progress = logger.create_progress_bar("Test progress")

        assert progress is not None


class TestWorkflowLogger:
    """测试工作流程日志管理器"""

    def setup_method(self):
        """设置测试方法"""
        self.base_logger = MagicMock(spec=Logger)
        self.workflow_logger = WorkflowLogger(self.base_logger)

    def test_workflow_logger_init(self):
        """测试初始化"""
        assert self.workflow_logger.logger == self.base_logger
        assert self.workflow_logger.current_step == 0
        assert self.workflow_logger.total_steps == 0
        assert self.workflow_logger.step_descriptions == []

    def test_start_workflow(self):
        """测试开始工作流程"""
        steps = ["Step 1", "Step 2", "Step 3"]

        self.workflow_logger.start_workflow(steps)

        assert self.workflow_logger.total_steps == 3
        assert self.workflow_logger.step_descriptions == steps
        assert self.workflow_logger.current_step == 0

        # 验证调用了日志方法
        self.base_logger.section.assert_called_once()
        self.base_logger.print_summary.assert_called_once()

    def test_start_step(self):
        """测试开始步骤"""
        steps = ["Step 1", "Step 2"]
        self.workflow_logger.start_workflow(steps)

        self.workflow_logger.start_step(0)

        assert self.workflow_logger.current_step == 1
        self.base_logger.step.assert_called_once()

    def test_complete_step(self):
        """测试完成步骤"""
        steps = ["Step 1", "Step 2"]
        self.workflow_logger.start_workflow(steps)

        self.workflow_logger.complete_step(0, "Success result")

        self.base_logger.success.assert_called_once()
        call_args = self.base_logger.success.call_args[0][0]
        assert "Step 1" in call_args
        assert "Success result" in call_args

    def test_complete_step_without_result(self):
        """测试完成步骤（无结果）"""
        steps = ["Step 1"]
        self.workflow_logger.start_workflow(steps)

        self.workflow_logger.complete_step(0)

        self.base_logger.success.assert_called_once()
        call_args = self.base_logger.success.call_args[0][0]
        assert "Step 1" in call_args

    def test_fail_step(self):
        """测试步骤失败"""
        steps = ["Step 1"]
        self.workflow_logger.start_workflow(steps)

        error = Exception("Test error")
        self.workflow_logger.fail_step(0, error)

        self.base_logger.error.assert_called_once()
        self.base_logger.print_error_details.assert_called_once_with(error)

    def test_complete_workflow_success(self):
        """测试成功完成工作流程"""
        summary = {"files": 3, "time": "30s"}

        self.workflow_logger.complete_workflow(True, summary)

        self.base_logger.section.assert_called_once()
        self.base_logger.print_summary.assert_called_once()

    def test_complete_workflow_failure(self):
        """测试失败完成工作流程"""
        self.workflow_logger.complete_workflow(False)

        self.base_logger.section.assert_called_once()
        # 失败时不应该调用 print_summary
        self.base_logger.print_summary.assert_not_called()

    def test_step_index_out_of_range(self):
        """测试步骤索引超出范围"""
        steps = ["Step 1"]
        self.workflow_logger.start_workflow(steps)

        # 这些调用不应该引发异常
        self.workflow_logger.start_step(5)
        self.workflow_logger.complete_step(5)
        self.workflow_logger.fail_step(5, Exception("Test"))

        # 验证没有调用相关方法
        self.base_logger.step.assert_not_called()


class TestLoggerFactories:
    """测试日志工厂函数"""

    def test_get_logger_default(self):
        """测试获取默认日志器"""
        logger = get_logger()

        assert isinstance(logger, Logger)
        assert logger.name == "aider-automation"

    def test_get_logger_with_params(self):
        """测试带参数获取日志器"""
        logger = get_logger(
            name="test",
            level="DEBUG",
            verbose=True
        )

        assert isinstance(logger, Logger)
        assert logger.name == "test"
        assert logger.verbose is True

    def test_get_workflow_logger_default(self):
        """测试获取默认工作流程日志器"""
        workflow_logger = get_workflow_logger()

        assert isinstance(workflow_logger, WorkflowLogger)
        assert isinstance(workflow_logger.logger, Logger)

    def test_get_workflow_logger_with_logger(self):
        """测试带日志器获取工作流程日志器"""
        base_logger = Logger(name="test")
        workflow_logger = get_workflow_logger(base_logger)

        assert isinstance(workflow_logger, WorkflowLogger)
        assert workflow_logger.logger == base_logger