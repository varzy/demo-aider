"""核心数据模型定义"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class GitHubConfig(BaseModel):
    """GitHub 配置"""
    token: str = Field(..., description="GitHub API token")
    repo: str = Field(..., description="GitHub 仓库 (owner/repo)")

    @field_validator('repo')
    @classmethod
    def validate_repo_format(cls, v):
        """验证仓库格式为 owner/repo"""
        if '/' not in v or v.count('/') != 1:
            raise ValueError('GitHub 仓库格式必须为 owner/repo')
        owner, repo = v.split('/')
        if not owner or not repo:
            raise ValueError('GitHub 仓库的 owner 和 repo 名称不能为空')
        return v


class AiderConfig(BaseModel):
    """Aider 配置"""
    options: List[str] = Field(default_factory=list, description="Aider 命令行选项")
    model: Optional[str] = Field(default=None, description="Aider 使用的模型")


class GitConfig(BaseModel):
    """Git 配置"""
    default_branch: str = Field(default="main", description="默认分支名称")
    branch_prefix: str = Field(default="aider-automation/", description="分支名称前缀")

    @field_validator('branch_prefix')
    @classmethod
    def validate_branch_prefix(cls, v):
        """验证分支前缀格式"""
        if v and not v.endswith('/'):
            return v + '/'
        return v


class TemplateConfig(BaseModel):
    """模板配置"""
    commit_message: str = Field(
        default="feat: {summary}",
        description="提交信息模板"
    )
    pr_title: str = Field(
        default="AI-generated changes: {summary}",
        description="PR 标题模板"
    )
    pr_body: str = Field(
        default="""## 自动生成的更改

**提示词：** {prompt}

**修改的文件：**
{modified_files}

**Aider 摘要：**
{aider_summary}""",
        description="PR 描述模板"
    )


class Config(BaseModel):
    """主配置数据模型"""

    github: GitHubConfig = Field(..., description="GitHub 配置")
    aider: AiderConfig = Field(default_factory=AiderConfig, description="Aider 配置")
    git: GitConfig = Field(default_factory=GitConfig, description="Git 配置")
    templates: TemplateConfig = Field(default_factory=TemplateConfig, description="模板配置")

    # 向后兼容的属性
    @property
    def github_token(self) -> str:
        """获取 GitHub token（向后兼容）"""
        return self.github.token

    @property
    def github_repo(self) -> str:
        """获取 GitHub 仓库（向后兼容）"""
        return self.github.repo

    @property
    def aider_options(self) -> List[str]:
        """获取 Aider 选项（向后兼容）"""
        return self.aider.options

    @property
    def default_branch(self) -> str:
        """获取默认分支（向后兼容）"""
        return self.git.default_branch

    @property
    def commit_message_template(self) -> str:
        """获取提交信息模板（向后兼容）"""
        return self.templates.commit_message

    @property
    def pr_title_template(self) -> str:
        """获取 PR 标题模板（向后兼容）"""
        return self.templates.pr_title

    @property
    def pr_body_template(self) -> str:
        """获取 PR 描述模板（向后兼容）"""
        return self.templates.pr_body


@dataclass
class AiderResult:
    """Aider 执行结果"""
    success: bool
    modified_files: List[str] = field(default_factory=list)
    summary: str = ""
    error_message: Optional[str] = None
    output: str = ""


@dataclass
class PRResult:
    """Pull Request 创建结果"""
    success: bool
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowState:
    """工作流程状态"""
    prompt: str
    branch_name: str
    config: Config
    aider_result: Optional[AiderResult] = None
    commit_hash: Optional[str] = None
    pr_result: Optional[PRResult] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        """计算执行时长（秒）"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None