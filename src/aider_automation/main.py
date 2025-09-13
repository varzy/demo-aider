"""主脚本和命令行接口"""

import sys
from pathlib import Path
from typing import Optional

import click

from .config import ConfigManager
from .logger import get_logger, get_workflow_logger
from .error_handler import ErrorHandler
from .exceptions import AiderAutomationError
from .workflow import AiderAutomationWorkflow


@click.command()
@click.argument('prompt', required=False)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='配置文件路径'
)
@click.option(
    '--branch', '-b',
    help='分支名称（可选）'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='启用详细输出'
)
@click.option(
    '--log-file',
    type=click.Path(),
    help='日志文件路径'
)
@click.option(
    '--init',
    is_flag=True,
    help='创建默认配置文件'
)
@click.option(
    '--check',
    is_flag=True,
    help='检查环境和依赖项'
)
@click.option(
    '--force',
    is_flag=True,
    help='强制覆盖已存在的文件'
)
@click.version_option(version='0.1.0', prog_name='aider-automation')
def cli(
    prompt: Optional[str],
    config: Optional[str],
    branch: Optional[str],
    verbose: bool,
    log_file: Optional[str],
    init: bool,
    check: bool,
    force: bool
):
    """
    Aider 自动化脚本 - 集成 aider、Git 和 GitHub API 的自动化工具

    PROMPT: 要执行的提示词

    示例:

    \b
    # 基本使用
    aider-automation "添加用户认证功能"

    \b
    # 指定分支名称
    aider-automation "修复登录bug" --branch fix-login-bug

    \b
    # 使用自定义配置文件
    aider-automation "优化性能" --config my-config.json

    \b
    # 创建默认配置文件
    aider-automation --init

    \b
    # 检查环境
    aider-automation --check
    """
    # 设置日志
    logger = get_logger(
        level="DEBUG" if verbose else "INFO",
        verbose=verbose,
        log_file=log_file
    )

    error_handler = ErrorHandler(logger)

    try:
        # 处理初始化命令
        if init:
            handle_init_command(config, force, logger)
            return

        # 处理检查命令
        if check:
            handle_check_command(config, logger)
            return

        # 验证提示词
        if not prompt:
            logger.error("错误: 缺少提示词参数")
            logger.info("使用 'aider-automation --help' 查看使用说明")
            sys.exit(1)

        # 执行主工作流程
        handle_main_workflow(prompt, config, branch, logger, error_handler)

    except AiderAutomationError as e:
        error_report = error_handler.handle_error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n操作被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"发生未预期的错误: {e}")
        if verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)


def handle_init_command(config_path: Optional[str], force: bool, logger):
    """处理初始化命令"""
    logger.section("初始化配置文件")

    try:
        config_manager = ConfigManager(config_path)
        created_path = config_manager.create_default_config_file(overwrite=force)

        logger.success(f"配置文件已创建: {created_path}")
        logger.info("请编辑配置文件并设置您的 GitHub token 和仓库信息")

        # 显示配置示例
        logger.section("配置示例")
        example_config = config_manager.get_default_config()

        import json
        config_json = json.dumps(example_config, indent=2, ensure_ascii=False)
        logger.console.print(config_json, style="dim")

        logger.info("\n💡 提示:")
        logger.info("1. 设置环境变量 GITHUB_TOKEN 或直接在配置文件中填写")
        logger.info("2. 修改 github.repo 为您的仓库 (owner/repo)")
        logger.info("3. 根据需要调整其他配置选项")

    except Exception as e:
        logger.error(f"创建配置文件失败: {e}")
        sys.exit(1)


def handle_check_command(config_path: Optional[str], logger):
    """处理检查命令"""
    logger.section("环境检查")

    try:
        # 检查配置
        logger.step("检查配置文件")
        config_manager = ConfigManager(config_path)

        try:
            config = config_manager.load_config()
            config_manager.validate_config(config)
            logger.success("配置文件检查通过")
        except Exception as e:
            logger.error(f"配置检查失败: {e}")
            return

        # 检查依赖项
        logger.step("检查依赖项")
        from .dependencies import DependencyChecker

        dependency_checker = DependencyChecker()
        missing_deps = dependency_checker.check_all_dependencies(config)

        if not missing_deps:
            logger.success("所有依赖项检查通过")
        else:
            logger.error("发现缺失的依赖项:")
            for dep in missing_deps:
                logger.console.print(f"  ❌ {dep}", style="red")
            return

        # 获取详细信息
        logger.step("获取工具信息")
        dep_info = dependency_checker.get_dependency_info()

        logger.print_summary("工具信息", [
            f"Aider: {dep_info.get('aider', {}).get('version', 'N/A')}",
            f"Git: {dep_info.get('git', {}).get('version', 'N/A')}",
            f"Git 仓库: {'是' if dep_info.get('git', {}).get('repository') else '否'}",
            f"远程仓库: {'是' if dep_info.get('git', {}).get('remote') else '否'}"
        ])

        logger.success("✅ 环境检查完成，所有组件正常工作")

    except Exception as e:
        logger.error(f"环境检查失败: {e}")
        sys.exit(1)


def handle_main_workflow(
    prompt: str,
    config_path: Optional[str],
    branch: Optional[str],
    logger,
    error_handler: ErrorHandler
):
    """处理主工作流程"""
    logger.section("开始 Aider 自动化工作流程")

    try:
        # 加载配置
        config_manager = ConfigManager(config_path)
        config = config_manager.load_config()

        # 创建工作流程
        workflow = AiderAutomationWorkflow(config, logger)

        # 执行工作流程
        result = workflow.execute(prompt, branch)

        if result.success:
            logger.section("🎉 工作流程执行成功")

            # 显示执行摘要
            summary_items = [
                f"分支: {result.branch_name}",
                f"提交: {result.commit_hash[:8] if result.commit_hash else 'N/A'}",
                f"修改文件: {len(result.aider_result.modified_files) if result.aider_result else 0}",
                f"执行时间: {result.duration:.1f}秒" if result.duration else "N/A"
            ]

            if result.pr_result and result.pr_result.success:
                summary_items.append(f"PR: {result.pr_result.pr_url}")

            logger.print_summary("执行摘要", summary_items)

            if result.pr_result and result.pr_result.success:
                logger.success(f"🔗 Pull Request 已创建: {result.pr_result.pr_url}")

        else:
            logger.section("❌ 工作流程执行失败")
            if result.error:
                error_handler.handle_error(result.error)
            sys.exit(1)

    except Exception as e:
        error_handler.handle_error(e, "执行主工作流程时")
        sys.exit(1)


if __name__ == '__main__':
    cli()