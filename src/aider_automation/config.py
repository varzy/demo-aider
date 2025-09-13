"""配置管理器"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import ValidationError

from .models import Config, GitHubConfig, AiderConfig, GitConfig, TemplateConfig
from .exceptions import ConfigurationError


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG_FILENAME = ".aider-automation.json"

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_FILENAME

    def load_config(self) -> Config:
        """
        加载配置文件

        Returns:
            Config: 配置对象

        Raises:
            ConfigurationError: 配置文件不存在或格式错误
        """
        config_file = Path(self.config_path)

        if not config_file.exists():
            raise ConfigurationError(
                f"配置文件不存在: {config_file.absolute()}",
                f"请创建配置文件或运行 'aider-automation --init' 生成默认配置"
            )

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"配置文件 JSON 格式错误: {e}",
                f"请检查 {config_file.absolute()} 的 JSON 语法"
            )
        except Exception as e:
            raise ConfigurationError(
                f"读取配置文件失败: {e}",
                f"请检查 {config_file.absolute()} 的文件权限"
            )

        # 替换环境变量
        processed_config = self._substitute_env_vars(raw_config)

        # 验证和创建配置对象
        try:
            return self._create_config_from_dict(processed_config)
        except ValidationError as e:
            raise ConfigurationError(
                f"配置验证失败: {self._format_validation_error(e)}",
                "请检查配置文件格式和必需字段"
            )

    def validate_config(self, config: Config) -> bool:
        """
        验证配置对象

        Args:
            config: 要验证的配置对象

        Returns:
            bool: 验证是否通过

        Raises:
            ConfigurationError: 配置验证失败
        """
        try:
            # 验证 GitHub token 不为空
            if not config.github.token.strip():
                raise ConfigurationError(
                    "GitHub token 不能为空",
                    "请设置有效的 GitHub token"
                )

            # 验证仓库格式
            if '/' not in config.github.repo:
                raise ConfigurationError(
                    "GitHub 仓库格式错误",
                    "仓库格式应为 'owner/repo'"
                )

            return True
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"配置验证失败: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置字典

        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            "github": {
                "token": "${GITHUB_TOKEN}",
                "repo": "owner/repository-name"
            },
            "aider": {
                "options": ["--no-pretty", "--yes"],
                "model": "gpt-4"
            },
            "git": {
                "default_branch": "main",
                "branch_prefix": "aider-automation/"
            },
            "templates": {
                "commit_message": "feat: {summary}",
                "pr_title": "AI-generated changes: {summary}",
                "pr_body": "## 自动生成的更改\n\n**提示词：** {prompt}\n\n**修改的文件：**\n{modified_files}\n\n**Aider 摘要：**\n{aider_summary}"
            }
        }

    def create_default_config_file(self, overwrite: bool = False) -> Path:
        """
        创建默认配置文件

        Args:
            overwrite: 是否覆盖已存在的文件

        Returns:
            Path: 创建的配置文件路径

        Raises:
            ConfigurationError: 文件已存在且不允许覆盖
        """
        config_file = Path(self.config_path)

        if config_file.exists() and not overwrite:
            raise ConfigurationError(
                f"配置文件已存在: {config_file.absolute()}",
                "使用 --force 参数强制覆盖"
            )

        default_config = self.get_default_config()

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(
                f"创建配置文件失败: {e}",
                f"请检查目录 {config_file.parent.absolute()} 的写入权限"
            )

        return config_file

    def _substitute_env_vars(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归替换配置中的环境变量

        Args:
            config_dict: 配置字典

        Returns:
            Dict[str, Any]: 替换后的配置字典
        """
        if isinstance(config_dict, dict):
            return {k: self._substitute_env_vars(v) for k, v in config_dict.items()}
        elif isinstance(config_dict, list):
            return [self._substitute_env_vars(item) for item in config_dict]
        elif isinstance(config_dict, str):
            return self._substitute_env_var_string(config_dict)
        else:
            return config_dict

    def _substitute_env_var_string(self, value: str) -> str:
        """
        替换字符串中的环境变量

        Args:
            value: 包含环境变量的字符串

        Returns:
            str: 替换后的字符串
        """
        # 匹配 ${VAR_NAME} 格式的环境变量
        pattern = r'\$\{([^}]+)\}'

        def replace_var(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is None:
                raise ConfigurationError(
                    f"环境变量 {var_name} 未设置",
                    f"请设置环境变量 {var_name} 或在配置文件中直接指定值"
                )
            return env_value

        return re.sub(pattern, replace_var, value)

    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> Config:
        """
        从字典创建配置对象

        Args:
            config_dict: 配置字典

        Returns:
            Config: 配置对象
        """
        # 创建子配置对象
        github_config = GitHubConfig(**config_dict.get('github', {}))
        aider_config = AiderConfig(**config_dict.get('aider', {}))
        git_config = GitConfig(**config_dict.get('git', {}))
        templates_config = TemplateConfig(**config_dict.get('templates', {}))

        return Config(
            github=github_config,
            aider=aider_config,
            git=git_config,
            templates=templates_config
        )

    def _format_validation_error(self, error: ValidationError) -> str:
        """
        格式化验证错误信息

        Args:
            error: Pydantic 验证错误

        Returns:
            str: 格式化的错误信息
        """
        errors = []
        for err in error.errors():
            field = '.'.join(str(loc) for loc in err['loc'])
            message = err['msg']
            errors.append(f"{field}: {message}")
        return '; '.join(errors)