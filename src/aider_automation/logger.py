"""统一日志管理器"""

import logging
import sys
from pathlib import Path
from typing import Optional, TextIO
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text


class Logger:
    """统一日志管理器"""

    def __init__(
        self,
        name: str = "aider-automation",
        level: str = "INFO",
        verbose: bool = False,
        log_file: Optional[str] = None
    ):
        """
        初始化日志管理器

        Args:
            name: 日志器名称
            level: 日志级别
            verbose: 是否启用详细模式
            log_file: 日志文件路径（可选）
        """
        self.name = name
        self.verbose = verbose
        self.console = Console()

        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 清除现有处理器
        self.logger.handlers.clear()

        # 添加控制台处理器
        self._setup_console_handler()

        # 添加文件处理器（如果指定）
        if log_file:
            self._setup_file_handler(log_file)

    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = RichHandler(
            console=self.console,
            show_time=False,
            show_path=False,
            rich_tracebacks=True
        )

        # 设置格式
        if self.verbose:
            formatter = logging.Formatter(
                "%(levelname)s - %(name)s - %(message)s"
            )
        else:
            formatter = logging.Formatter("%(message)s")

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_file_handler(self, log_file: str):
        """设置文件处理器"""
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 文件日志使用详细格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, **kwargs)

    def success(self, message: str):
        """记录成功信息"""
        self.console.print(f"✅ {message}", style="green")

    def step(self, message: str):
        """记录步骤信息"""
        self.console.print(f"🔄 {message}", style="blue")

    def progress(self, message: str):
        """显示进度信息"""
        self.console.print(f"⏳ {message}", style="yellow")

    def section(self, title: str):
        """显示章节标题"""
        self.console.print(f"\n📋 {title}", style="bold cyan")
        self.console.print("─" * (len(title) + 4), style="cyan")

    def print_summary(self, title: str, items: list):
        """打印摘要信息"""
        self.console.print(f"\n📊 {title}", style="bold magenta")
        for item in items:
            self.console.print(f"  • {item}")

    def print_error_details(self, error: Exception, suggestions: Optional[list] = None):
        """打印错误详情"""
        self.console.print(f"\n❌ 错误: {error}", style="bold red")

        if hasattr(error, 'details') and error.details:
            self.console.print(f"详情: {error.details}", style="red")

        if suggestions:
            self.console.print("\n💡 建议解决方案:", style="yellow")
            for suggestion in suggestions:
                self.console.print(f"  • {suggestion}", style="yellow")

    def create_progress_bar(self, description: str = "处理中...") -> Progress:
        """创建进度条"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )


class WorkflowLogger:
    """工作流程日志管理器"""

    def __init__(self, logger: Logger):
        """
        初始化工作流程日志管理器

        Args:
            logger: 基础日志管理器
        """
        self.logger = logger
        self.current_step = 0
        self.total_steps = 0
        self.step_descriptions = []

    def start_workflow(self, steps: list):
        """
        开始工作流程

        Args:
            steps: 步骤描述列表
        """
        self.total_steps = len(steps)
        self.step_descriptions = steps
        self.current_step = 0

        self.logger.section("开始执行工作流程")
        self.logger.print_summary("执行步骤", steps)

    def start_step(self, step_index: int):
        """
        开始执行步骤

        Args:
            step_index: 步骤索引
        """
        if step_index < len(self.step_descriptions):
            self.current_step = step_index + 1
            description = self.step_descriptions[step_index]
            self.logger.step(f"步骤 {self.current_step}/{self.total_steps}: {description}")

    def complete_step(self, step_index: int, result: Optional[str] = None):
        """
        完成步骤

        Args:
            step_index: 步骤索引
            result: 步骤结果描述
        """
        if step_index < len(self.step_descriptions):
            description = self.step_descriptions[step_index]
            if result:
                self.logger.success(f"完成: {description} - {result}")
            else:
                self.logger.success(f"完成: {description}")

    def fail_step(self, step_index: int, error: Exception):
        """
        步骤失败

        Args:
            step_index: 步骤索引
            error: 错误信息
        """
        if step_index < len(self.step_descriptions):
            description = self.step_descriptions[step_index]
            self.logger.error(f"步骤失败: {description}")
            self.logger.print_error_details(error)

    def complete_workflow(self, success: bool, summary: Optional[dict] = None):
        """
        完成工作流程

        Args:
            success: 是否成功
            summary: 执行摘要
        """
        if success:
            self.logger.section("工作流程执行成功")
            if summary:
                summary_items = []
                for key, value in summary.items():
                    summary_items.append(f"{key}: {value}")
                self.logger.print_summary("执行摘要", summary_items)
        else:
            self.logger.section("工作流程执行失败")


def get_logger(
    name: str = "aider-automation",
    level: str = "INFO",
    verbose: bool = False,
    log_file: Optional[str] = None
) -> Logger:
    """
    获取日志管理器实例

    Args:
        name: 日志器名称
        level: 日志级别
        verbose: 是否启用详细模式
        log_file: 日志文件路径

    Returns:
        Logger: 日志管理器实例
    """
    return Logger(name, level, verbose, log_file)


def get_workflow_logger(logger: Optional[Logger] = None) -> WorkflowLogger:
    """
    获取工作流程日志管理器

    Args:
        logger: 基础日志管理器，如果为 None 则创建默认的

    Returns:
        WorkflowLogger: 工作流程日志管理器
    """
    if logger is None:
        logger = get_logger()

    return WorkflowLogger(logger)