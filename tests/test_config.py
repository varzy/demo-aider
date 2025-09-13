"""测试配置管理器"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from aider_automation.config import ConfigManager
from aider_automation.models import Config
from aider_automation.exceptions import ConfigurationError


class TestConfigManager:
    """测试配置管理器"""

    def test_load_valid_config(self):
        """测试加载有效配置"""
        config_data = {
            "github": {
                "token": "test_token",
                "repo": "owner/repo"
            },
            "aider": {
                "options": ["--no-pretty"],
                "model": "gpt-4"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            assert isinstance(config, Config)
            assert config.github.token == "test_token"
            assert config.github.repo == "owner/repo"
            assert config.aider.options == ["--no-pretty"]
            assert config.aider.model == "gpt-4"
        finally:
            os.unlink(config_path)

    def test_load_config_with_env_vars(self):
        """测试加载包含环境变量的配置"""
        config_data = {
            "github": {
                "token": "${TEST_GITHUB_TOKEN}",
                "repo": "owner/repo"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            with patch.dict(os.environ, {'TEST_GITHUB_TOKEN': 'env_token'}):
                manager = ConfigManager(config_path)
                config = manager.load_config()

                assert config.github.token == "env_token"
        finally:
            os.unlink(config_path)

    def test_load_config_missing_env_var(self):
        """测试加载配置时环境变量缺失"""
        config_data = {
            "github": {
                "token": "${MISSING_TOKEN}",
                "repo": "owner/repo"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config()

            assert "环境变量 MISSING_TOKEN 未设置" in str(exc_info.value)
        finally:
            os.unlink(config_path)

    def test_load_config_file_not_found(self):
        """测试配置文件不存在"""
        manager = ConfigManager("nonexistent.json")

        with pytest.raises(ConfigurationError) as exc_info:
            manager.load_config()

        assert "配置文件不存在" in str(exc_info.value)

    def test_load_config_invalid_json(self):
        """测试无效的 JSON 配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config()

            assert "JSON 格式错误" in str(exc_info.value)
        finally:
            os.unlink(config_path)

    def test_validate_config_success(self):
        """测试配置验证成功"""
        config_data = {
            "github": {
                "token": "valid_token",
                "repo": "owner/repo"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            assert manager.validate_config(config) is True
        finally:
            os.unlink(config_path)

    def test_validate_config_empty_token(self):
        """测试空 token 验证失败"""
        config_data = {
            "github": {
                "token": "  ",  # 空白字符
                "repo": "owner/repo"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            with pytest.raises(ConfigurationError) as exc_info:
                manager.validate_config(config)

            assert "GitHub token 不能为空" in str(exc_info.value)
        finally:
            os.unlink(config_path)

    def test_validate_config_invalid_repo_format(self):
        """测试无效仓库格式验证失败"""
        config_data = {
            "github": {
                "token": "valid_token",
                "repo": "invalid_repo_format"  # 缺少 /
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)

            with pytest.raises(ConfigurationError) as exc_info:
                manager.load_config()

            assert "GitHub 仓库格式必须为 owner/repo" in str(exc_info.value)
        finally:
            os.unlink(config_path)

    def test_get_default_config(self):
        """测试获取默认配置"""
        manager = ConfigManager()
        default_config = manager.get_default_config()

        assert isinstance(default_config, dict)
        assert "github" in default_config
        assert "aider" in default_config
        assert "git" in default_config
        assert "templates" in default_config

        assert default_config["github"]["token"] == "${GITHUB_TOKEN}"
        assert default_config["git"]["default_branch"] == "main"

    def test_create_default_config_file(self):
        """测试创建默认配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = ConfigManager(str(config_path))

            created_path = manager.create_default_config_file()

            assert created_path.exists()
            assert created_path == config_path

            # 验证文件内容
            with open(created_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            assert "github" in config_data
            assert config_data["github"]["token"] == "${GITHUB_TOKEN}"

    def test_create_default_config_file_exists(self):
        """测试创建配置文件时文件已存在"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{}")
            config_path = f.name

        try:
            manager = ConfigManager(config_path)

            with pytest.raises(ConfigurationError) as exc_info:
                manager.create_default_config_file()

            assert "配置文件已存在" in str(exc_info.value)
        finally:
            os.unlink(config_path)

    def test_create_default_config_file_overwrite(self):
        """测试强制覆盖已存在的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{}")
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            created_path = manager.create_default_config_file(overwrite=True)

            assert created_path.exists()

            # 验证文件被覆盖
            with open(created_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            assert "github" in config_data
        finally:
            os.unlink(config_path)


class TestConfigModels:
    """测试配置数据模型"""

    def test_config_backward_compatibility(self):
        """测试配置对象的向后兼容性"""
        config_data = {
            "github": {
                "token": "test_token",
                "repo": "owner/repo"
            },
            "aider": {
                "options": ["--no-pretty"],
                "model": "gpt-4"
            },
            "git": {
                "default_branch": "develop",
                "branch_prefix": "feature/"
            },
            "templates": {
                "commit_message": "chore: {summary}",
                "pr_title": "Auto: {summary}",
                "pr_body": "Changes: {prompt}"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            config = manager.load_config()

            # 测试向后兼容的属性
            assert config.github_token == "test_token"
            assert config.github_repo == "owner/repo"
            assert config.aider_options == ["--no-pretty"]
            assert config.default_branch == "develop"
            assert config.commit_message_template == "chore: {summary}"
            assert config.pr_title_template == "Auto: {summary}"
            assert config.pr_body_template == "Changes: {prompt}"
        finally:
            os.unlink(config_path)

    def test_branch_prefix_validation(self):
        """测试分支前缀验证"""
        from aider_automation.models import GitConfig

        # 测试自动添加斜杠
        git_config = GitConfig(branch_prefix="feature")
        assert git_config.branch_prefix == "feature/"

        # 测试已有斜杠的情况
        git_config = GitConfig(branch_prefix="feature/")
        assert git_config.branch_prefix == "feature/"