# 🎯 WoodenMan 项目实战指南

## 目标
使用 aider-automation 为 WoodenMan 项目的 index.html 更换背景色

## 📋 准备工作清单

### 1. 确认项目信息
- **项目路径**：`/Users/zy/Developer/WoodenMan`
- **需求**：更换 index.html 的背景色
- **GitHub 仓库**：需要确认你的 GitHub 仓库地址

### 2. 需要准备的信息
- [ ] GitHub 仓库名称（格式：用户名/仓库名）
- [ ] GitHub Token（用于创建 PR）
- [ ] 确认项目是 Git 仓库且已推送到 GitHub

## 🚀 第一步：检查 WoodenMan 项目状态

```bash
# 进入 WoodenMan 项目目录
cd /Users/zy/Developer/WoodenMan

# 检查是否是 Git 仓库
git status

# 查看远程仓库信息
git remote -v

# 查看项目文件结构
ls -la
```

**预期结果：**
- 应该看到 `.git` 目录
- 应该有 `index.html` 文件
- 应该有远程仓库地址（类似 `https://github.com/用户名/WoodenMan.git`）

## 🔧 第二步：在 aider-automation 项目中配置

```bash
# 回到 aider-automation 项目目录
cd /Users/zy/Developer/demo-aider

# 激活虚拟环境
source venv/bin/activate

# 运行设置向导
python setup.py
```

**设置向导中的回答示例：**
```
1. GitHub 仓库信息
   请输入你的 GitHub 仓库: zy/WoodenMan
   # 注意：这里要填写你实际的 GitHub 用户名和仓库名

2. GitHub Token
   选择 (a/b): a
   # 选择使用环境变量（推荐）

3. AI 模型选择
   选择 (1-4): 1
   # 选择 gpt-4（如果你有 OpenAI API）

4. Git 分支设置
   默认分支名称 (默认: main): main
   分支前缀 (默认: aider-automation/): bg-change/
   # 使用更有意义的前缀
```

## 🔑 第三步：设置 GitHub Token

### 获取 GitHub Token：
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. Token 名称：`aider-automation-woodenman`
4. 勾选权限：`repo`（完整仓库访问）
5. 点击 "Generate token"
6. 复制生成的 token（以 `ghp_` 开头）

### 设置环境变量：
```bash
# 设置 GitHub Token
export GITHUB_TOKEN="ghp_你的实际token"

# 验证设置
echo $GITHUB_TOKEN
```

## ✅ 第四步：验证配置

```bash
# 检查配置是否正确
python check_setup.py
```

**预期输出：**
```
🔍 Aider Automation 环境检查
========================================

📁 文件检查:
✅ 配置文件: .aider-automation.json

⚙️  配置检查:
✅ 配置文件: .aider-automation.json
   ✅ 配置格式正确

🔑 环境变量检查:
✅ GitHub Token: 已设置 (ghp_L3HyJn...)

🛠️  工具检查:
✅ Python: Python 3.13.7
✅ Git: git version 2.39.5
✅ Aider: aider 0.86.1

📦 Python 包检查:
✅ Click: 已安装
✅ Requests: 已安装
✅ Rich: 已安装

========================================
🎉 所有检查通过！你可以开始使用 aider-automation 了
```

## 🎨 第五步：执行背景色更换任务

### 方法一：切换到 WoodenMan 目录执行
```bash
# 切换到 WoodenMan 项目目录
cd /Users/zy/Developer/WoodenMan

# 执行 aider-automation（使用绝对路径）
python /Users/zy/Developer/demo-aider/src/aider_automation/main.py "将 index.html 的背景色改为淡蓝色 (#e3f2fd)"
```

### 方法二：在 aider-automation 目录执行（推荐）
```bash
# 确保在 aider-automation 目录
cd /Users/zy/Developer/demo-aider

# 激活虚拟环境
source venv/bin/activate

# 使用 --config 指定配置，在 WoodenMan 目录执行
cd /Users/zy/Developer/WoodenMan &&
python /Users/zy/Developer/demo-aider/venv/bin/python -m aider_automation.main "将 index.html 的背景色改为淡蓝色 (#e3f2fd)"
```

### 推荐的提示词示例：
```bash
# 基础版本
"将 index.html 的背景色改为淡蓝色"

# 详细版本
"将 index.html 的背景色从当前颜色改为淡蓝色 (#e3f2fd)，如果没有现有的背景色样式，请添加到 body 标签的 CSS 中"

# 更具体的版本
"修改 index.html 文件，将页面背景色设置为淡蓝色 (#e3f2fd)。如果文件中有内联样式，请修改现有的 background-color 属性；如果没有样式，请在 head 标签中添加 style 标签设置 body 的背景色"
```

## 📊 第六步：观察执行过程

执行命令后，你会看到类似这样的输出：

```
🚀 开始 Aider 自动化工作流程
================================================

📋 开始执行工作流程
────────────────────────────────────────────────
执行步骤:
  • 验证环境和依赖项
  • 创建或切换分支
  • 执行 Aider 代码修改
  • 提交更改到 Git
  • 推送分支到远程仓库
  • 创建 GitHub Pull Request

🔄 步骤 1/6: 验证环境和依赖项
⏳ 检查依赖项...
✅ 完成: 验证环境和依赖项 - 环境验证通过

🔄 步骤 2/6: 创建或切换分支
⏳ 处理分支...
✅ 完成: 创建或切换分支 - 分支: bg-change/change-background-color-20241213-143022

🔄 步骤 3/6: 执行 Aider 代码修改
⏳ 执行 Aider 代码修改...
✅ 完成: 执行 Aider 代码修改 - 修改了 1 个文件

🔄 步骤 4/6: 提交更改到 Git
⏳ 提交更改...
✅ 完成: 提交更改到 Git - 提交: abc12345

🔄 步骤 5/6: 推送分支到远程仓库
⏳ 推送分支到远程仓库...
✅ 完成: 推送分支到远程仓库 - 推送成功

🔄 步骤 6/6: 创建 GitHub Pull Request
⏳ 创建 Pull Request...
✅ 完成: 创建 GitHub Pull Request - PR #123

🎉 工作流程执行成功
================================================

📊 执行摘要
────────────────────────────────────────────────
  • 分支: bg-change/change-background-color-20241213-143022
  • 提交: abc12345
  • 修改文件: 1
  • 执行时间: 45.2秒
  • PR: https://github.com/zy/WoodenMan/pull/123

🔗 Pull Request 已创建: https://github.com/zy/WoodenMan/pull/123
```

## 🔍 第七步：检查结果

### 1. 检查本地文件变化
```bash
# 在 WoodenMan 目录中
cd /Users/zy/Developer/WoodenMan

# 查看当前分支
git branch

# 查看文件变化
git diff HEAD~1

# 查看修改的文件内容
cat index.html
```

### 2. 检查 GitHub PR
1. 打开输出中显示的 PR 链接
2. 查看代码变更
3. 确认背景色修改是否符合预期

### 3. 本地测试
```bash
# 在浏览器中打开 index.html 查看效果
open index.html
# 或
python -m http.server 8000
# 然后访问 http://localhost:8000
```

## 🎯 第八步：处理 PR

### 如果修改满意：
1. 在 GitHub 上审查 PR
2. 点击 "Merge pull request"
3. 选择合并方式（通常选择 "Squash and merge"）
4. 删除功能分支

### 如果需要调整：
1. 在本地继续修改文件
2. 提交新的更改：
   ```bash
   git add .
   git commit -m "调整背景色深度"
   git push
   ```
3. PR 会自动更新

### 清理本地分支：
```bash
# 切换回主分支
git checkout main

# 拉取最新代码
git pull origin main

# 删除本地功能分支
git branch -d bg-change/change-background-color-20241213-143022
```

## ❗ 可能遇到的问题和解决方案

### 问题 1：提示 "不是 Git 仓库"
```bash
cd /Users/zy/Developer/WoodenMan
git init
git remote add origin https://github.com/你的用户名/WoodenMan.git
```

### 问题 2：提示 "GitHub API 访问失败"
```bash
# 重新设置 token
export GITHUB_TOKEN="你的新token"

# 测试 token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### 问题 3：aider 找不到文件
确保在正确的目录中执行命令，或使用绝对路径。

### 问题 4：AI 修改不符合预期
使用更具体的提示词，例如：
```bash
"在 index.html 的 head 标签中添加 <style>body{background-color:#e3f2fd;}</style>"
```

## 🎉 成功标志

当你看到以下情况时，说明任务成功完成：

1. ✅ 命令执行无错误
2. ✅ 创建了新的 Git 分支
3. ✅ index.html 文件被修改
4. ✅ 在 GitHub 上创建了 PR
5. ✅ 本地浏览器中可以看到新的背景色

## 📝 总结

这个实战指南帮你：
1. 配置 aider-automation 连接到 WoodenMan 项目
2. 使用 AI 自动修改 index.html 的背景色
3. 自动创建 GitHub PR
4. 完成整个自动化工作流程

现在你可以按照这个指南一步步操作，实现你的第一个 AI 自动化代码修改任务！