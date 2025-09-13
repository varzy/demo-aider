# Aider Automation Script

一个集成 aider、Git 和 GitHub API 的自动化脚本，可以在任意项目中使用。通过简单的命令行调用，自动完成从代码修改到 PR 创建的整个工作流程。

## ✨ 功能特性

- 🤖 **智能代码修改** - 集成 aider AI 编程助手，根据自然语言提示修改代码
- 🔄 **自动 Git 操作** - 自动创建分支、提交更改、推送到远程仓库
- 🚀 **自动 PR 创建** - 自动创建 GitHub Pull Request，包含详细的描述
- ⚙️ **灵活配置系统** - 支持 JSON 配置文件和环境变量
- 🌿 **智能分支管理** - 自动生成分支名称，处理分支冲突
- 📝 **详细日志输出** - 美观的进度显示和详细的错误报告
- 🧪 **完整测试覆盖** - 190+ 测试用例，确保代码质量
- 🛡️ **错误处理** - 智能错误检测和恢复建议

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装（推荐）
pip install aider-automation

# 或从源码安装
git clone https://github.com/your-org/aider-automation
cd aider-automation
pip install -e ".[dev]"
```

### 前置要求

1. **aider** - AI 编程助手
   ```bash
   pip install aider-chat
   ```

2. **Git** - 版本控制工具
   ```bash
   # macOS
   brew install git

   # Ubuntu/Debian
   sudo apt-get install git
   ```

3. **GitHub Token** - 用于 API 访问
   - 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - 创建新 token，需要 `repo` 权限

### 基本使用

```bash
# 1. 初始化配置文件
aider-automation --init

# 2. 设置 GitHub token
export GITHUB_TOKEN="your_github_token_here"

# 3. 编辑配置文件，设置仓库信息
# 编辑 .aider-automation.json

# 4. 检查环境
aider-automation --check

# 5. 执行自动化任务
aider-automation "添加用户认证功能"
```

## ⚙️ 配置

### 配置文件示例

在项目根目录创建 `.aider-automation.json`：

```json
{
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
    "pr_body": "## 自动生成的更改\\n\\n**提示词：** {prompt}\\n\\n**修改的文件：**\\n{modified_files}\\n\\n**Aider 摘要：**\\n{aider_summary}"
  }
}
```

### 配置选项说明

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `github.token` | GitHub API token | `${GITHUB_TOKEN}` |
| `github.repo` | GitHub 仓库 (owner/repo) | 必需 |
| `aider.options` | aider 命令行选项 | `["--no-pretty", "--yes"]` |
| `aider.model` | AI 模型名称 | `null` |
| `git.default_branch` | 默认分支 | `"main"` |
| `git.branch_prefix` | 分支名称前缀 | `"aider-automation/"` |
| `templates.*` | 提交和 PR 模板 | 见上方示例 |

## 📖 使用示例

### 基本用法

```bash
# 添加新功能
aider-automation "添加用户登录功能"

# 修复 bug
aider-automation "修复登录页面的样式问题"

# 重构代码
aider-automation "重构用户服务，提高代码可读性"
```

### 高级用法

```bash
# 指定分支名称
aider-automation "优化数据库查询性能" --branch optimize-db-queries

# 使用自定义配置文件
aider-automation "添加单元测试" --config custom-config.json

# 启用详细输出
aider-automation "更新文档" --verbose

# 保存日志到文件
aider-automation "重构 API" --log-file automation.log
```

### 工作流程

1. **环境验证** - 检查 aider、Git、GitHub 访问权限
2. **分支管理** - 创建或切换到工作分支
3. **代码修改** - 使用 aider 根据提示词修改代码
4. **提交更改** - 自动添加和提交所有更改
5. **推送分支** - 推送到远程 GitHub 仓库
6. **创建 PR** - 自动创建 Pull Request

## 🛠️ 开发

### 安装开发环境

```bash
# 克隆仓库
git clone https://github.com/your-org/aider-automation
cd aider-automation

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\\Scripts\\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_config.py

# 生成覆盖率报告
pytest --cov=src/aider_automation --cov-report=html
```

### 代码质量

```bash
# 代码格式化
black src tests
isort src tests

# 代码检查
flake8 src tests
mypy src
```

## 🔧 故障排除

### 常见问题

**Q: aider 命令未找到**
```bash
# 安装 aider
pip install aider-chat

# 检查是否在 PATH 中
which aider
```

**Q: GitHub API 访问失败**
```bash
# 检查 token 是否设置
echo $GITHUB_TOKEN

# 验证 token 权限
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

**Q: Git 仓库未初始化**
```bash
# 初始化 Git 仓库
git init

# 添加远程仓库
git remote add origin https://github.com/owner/repo.git
```

### 获取帮助

```bash
# 查看帮助信息
aider-automation --help

# 检查环境状态
aider-automation --check

# 启用详细日志
aider-automation "your prompt" --verbose --log-file debug.log
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [aider](https://aider.chat/) - 优秀的 AI 编程助手
- [Click](https://click.palletsprojects.com/) - 命令行界面框架
- [Rich](https://rich.readthedocs.io/) - 美观的终端输出
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

---

**让 AI 帮你自动化代码开发流程！** 🚀