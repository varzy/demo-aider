"""工作流程协调器"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from .models import Config, WorkflowState, AiderResult, PRResult
from .dependencies import DependencyChecker
from .git_manager import GitManager
from .branch_strategy import BranchStrategy
from .aider_executor import AiderExecutor
from .github_integration import GitHubIntegrator
from .logger import Logger, WorkflowLogger
from .exceptions import AiderAutomationError


@dataclass
class WorkflowResult:
    """工作流程执行结果"""
    success: bool
    branch_name: Optional[str] = None
    commit_hash: Optional[str] = None
    aider_result: Optional[AiderResult] = None
    pr_result: Optional[PRResult] = None
    error: Optional[Exception] = None
    duration: Optional[float] = None


class AiderAutomationWorkflow:
    """Aider 自动化工作流程协调器"""

    def __init__(self, config: Config, logger: Logger):
        """
        初始化工作流程协调器

        Args:
            config: 配置对象
            logger: 日志管理器
        """
        self.config = config
        self.logger = logger
        self.workflow_logger = WorkflowLogger(logger)

        # 初始化组件
        self.dependency_checker = DependencyChecker()
        self.git_manager = GitManager()
        self.branch_strategy = BranchStrategy(self.git_manager, config.git.branch_prefix)
        self.aider_executor = AiderExecutor(config)
        self.github_integrator = GitHubIntegrator(config)

    def execute(self, prompt: str, branch_name: Optional[str] = None) -> WorkflowResult:
        """
        执行完整的工作流程

        Args:
            prompt: 用户提示词
            branch_name: 分支名称（可选）

        Returns:
            WorkflowResult: 执行结果
        """
        start_time = datetime.now()

        # 定义工作流程步骤
        steps = [
            "验证环境和依赖项",
            "创建或切换分支",
            "执行 Aider 代码修改",
            "提交更改到 Git",
            "推送分支到远程仓库",
            "创建 GitHub Pull Request"
        ]

        self.workflow_logger.start_workflow(steps)

        try:
            # 步骤 1: 验证环境
            self.workflow_logger.start_step(0)
            self._validate_environment()
            self.workflow_logger.complete_step(0, "环境验证通过")

            # 步骤 2: 处理分支
            self.workflow_logger.start_step(1)
            final_branch_name = self._handle_branch(prompt, branch_name)
            self.workflow_logger.complete_step(1, f"分支: {final_branch_name}")

            # 步骤 3: 执行 Aider
            self.workflow_logger.start_step(2)
            aider_result = self._execute_aider(prompt)
            self.workflow_logger.complete_step(2, f"修改了 {len(aider_result.modified_files)} 个文件")

            # 步骤 4: 提交更改
            self.workflow_logger.start_step(3)
            commit_hash = self._commit_changes(aider_result, prompt)
            self.workflow_logger.complete_step(3, f"提交: {commit_hash[:8]}")

            # 步骤 5: 推送分支
            self.workflow_logger.start_step(4)
            self._push_branch(final_branch_name)
            self.workflow_logger.complete_step(4, "推送成功")

            # 步骤 6: 创建 PR
            self.workflow_logger.start_step(5)
            pr_result = self._create_pull_request(final_branch_name, aider_result, prompt)
            if pr_result.success:
                self.workflow_logger.complete_step(5, f"PR #{pr_result.pr_number}")
            else:
                self.workflow_logger.complete_step(5, "PR 创建失败")

            # 计算执行时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 完成工作流程
            self.workflow_logger.complete_workflow(True, {
                "分支": final_branch_name,
                "提交": commit_hash[:8],
                "修改文件": len(aider_result.modified_files),
                "执行时间": f"{duration:.1f}秒",
                "PR": pr_result.pr_url if pr_result.success else "创建失败"
            })

            return WorkflowResult(
                success=True,
                branch_name=final_branch_name,
                commit_hash=commit_hash,
                aider_result=aider_result,
                pr_result=pr_result,
                duration=duration
            )

        except Exception as e:
            # 记录失败的步骤
            current_step = getattr(self.workflow_logger, 'current_step', 1) - 1
            if current_step >= 0:
                self.workflow_logger.fail_step(current_step, e)

            self.workflow_logger.complete_workflow(False)

            return WorkflowResult(
                success=False,
                error=e
            )

    def _validate_environment(self):
        """验证环境和依赖项"""
        self.logger.progress("检查依赖项...")

        # 验证依赖项
        self.dependency_checker.validate_environment(self.config)

        # 验证 Aider 环境
        self.aider_executor.validate_environment()

        # 验证 GitHub 访问
        if not self.github_integrator.validate_access():
            raise AiderAutomationError(
                "GitHub API 访问验证失败",
                "请检查 token 和网络连接"
            )

        self.logger.debug("环境验证完成")

    def _handle_branch(self, prompt: str, branch_name: Optional[str]) -> str:
        """处理分支创建或切换"""
        self.logger.progress("处理分支...")

        if branch_name:
            # 用户指定了分支名称
            final_branch_name = self.branch_strategy.handle_branch_conflict(branch_name, prompt)
        else:
            # 自动生成分支名称
            final_branch_name = self.branch_strategy.create_unique_branch(prompt)

        self.logger.debug(f"使用分支: {final_branch_name}")
        return final_branch_name

    def _execute_aider(self, prompt: str) -> AiderResult:
        """执行 Aider 代码修改"""
        self.logger.progress("执行 Aider 代码修改...")

        aider_result = self.aider_executor.execute(prompt)

        if not aider_result.success:
            raise AiderAutomationError(
                f"Aider 执行失败: {aider_result.error_message}",
                "请检查提示词和项目状态"
            )

        if not aider_result.modified_files:
            self.logger.warning("Aider 没有修改任何文件")
        else:
            self.logger.debug(f"Aider 修改了文件: {aider_result.modified_files}")

        return aider_result

    def _commit_changes(self, aider_result: AiderResult, prompt: str) -> str:
        """提交更改到 Git"""
        self.logger.progress("提交更改...")

        # 检查是否有更改
        if not self.git_manager.has_changes():
            self.logger.warning("没有检测到文件更改")

            # 检查是否 aider 已经自动提交了更改
            # 获取最近的提交信息来验证
            try:
                result = self.git_manager._run_git_command(["log", "-1", "--oneline"])
                if result.returncode == 0 and result.stdout.strip():
                    recent_commit = result.stdout.strip()
                    self.logger.info(f"检测到最近的提交: {recent_commit}")

                    # 获取最近提交的哈希
                    hash_result = self.git_manager._run_git_command(["rev-parse", "HEAD"])
                    if hash_result.returncode == 0:
                        commit_hash = hash_result.stdout.strip()
                        self.logger.info("Aider 可能已经自动提交了更改")
                        return commit_hash
            except Exception as e:
                self.logger.debug(f"检查最近提交时出错: {e}")

            # 如果没有找到最近的提交，创建一个空提交
            commit_message = self.config.templates.commit_message.format(
                summary="空提交 - 无文件更改"
            )
            return self.git_manager.commit_changes(commit_message, allow_empty=True)

        # 添加所有更改
        self.git_manager.add_all_changes()

        # 生成提交信息
        commit_message = self.config.templates.commit_message.format(
            summary=aider_result.summary or prompt[:50]
        )

        # 提交更改
        commit_hash = self.git_manager.commit_changes(commit_message)

        self.logger.debug(f"提交哈希: {commit_hash}")
        return commit_hash

    def _push_branch(self, branch_name: str):
        """推送分支到远程仓库"""
        self.logger.progress("推送分支到远程仓库...")

        self.git_manager.push_branch(branch_name)

        self.logger.debug(f"分支 {branch_name} 推送成功")

    def _create_pull_request(self, branch_name: str, aider_result: AiderResult, prompt: str) -> PRResult:
        """创建 GitHub Pull Request"""
        self.logger.progress("创建 Pull Request...")

        # 格式化 PR 标题和描述
        pr_title = self.github_integrator.format_pr_title(aider_result, prompt)
        pr_body = self.github_integrator.format_pr_body(aider_result, prompt)

        # 创建 PR
        pr_result = self.github_integrator.create_pull_request(
            branch_name=branch_name,
            title=pr_title,
            body=pr_body
        )

        if pr_result.success:
            self.logger.debug(f"PR 创建成功: {pr_result.pr_url}")
        else:
            self.logger.warning(f"PR 创建失败: {pr_result.error_message}")

        return pr_result


class AiderAutomationScript:
    """Aider 自动化脚本主类（向后兼容）"""

    def __init__(self, config: Config, logger: Optional[Logger] = None):
        """
        初始化脚本

        Args:
            config: 配置对象
            logger: 日志管理器（可选）
        """
        if logger is None:
            from .logger import get_logger
            logger = get_logger()

        self.workflow = AiderAutomationWorkflow(config, logger)

    def run(self, prompt: str, branch_name: Optional[str] = None) -> bool:
        """
        运行脚本

        Args:
            prompt: 用户提示词
            branch_name: 分支名称（可选）

        Returns:
            bool: 是否成功
        """
        result = self.workflow.execute(prompt, branch_name)
        return result.success