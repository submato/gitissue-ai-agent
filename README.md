# GitIssue AI Agent 🤖

> 🎯 **This Repository is Agent-Enabled!** Want to see it in action? [Create an issue with `bot` label](#try-it-on-this-repo) and watch the AI agent automatically process it!

[English](#english) | [中文](#chinese)

<a name="english"></a>

## English

> Automatically solve GitLab issues with AI - The first intelligent GitLab issue automation framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🚀 Try It Now!

**This repository has the agent enabled!** Experience the power of AI-driven issue resolution firsthand:

👉 **[Quick Test: Create an Issue](#try-it-on-this-repo)** - See the agent analyze, comment, and create PRs automatically!

---

### 🌟 Features

- 🤖 **Automatic Issue Resolution** - AI analyzes and solves GitLab/GitHub issues automatically
- 💬 **Intelligent Comments** - Ask for clarification by @mentioning issue authors when needed
- 🔧 **Auto MR/PR Creation** - Automatically creates merge/pull requests with fixes
- 📊 **Multi-Platform Support** - Handle issues from GitLab and GitHub
- 📁 **Multi-Project Support** - Handle issues across all your projects
- 🔌 **Pluggable AI Providers** - Support Claude, GPT-4, local LLMs, and more
- 🏷️ **Label-Driven Workflow** - Control automation with issue labels (auto-managed)
- 📈 **State Management** - Never process the same issue twice
- ⚡ **Dual Mode** - API mode for servers, MCP mode for Claude Code integration

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gitissue-ai-agent.git
cd gitissue-ai-agent

# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config/config.example.yaml config/config.yaml
```

#### Configuration

Edit `config/config.yaml`:

**For GitLab:**

```yaml
gitlab:
  url: "https://gitlab.com"
  access_token: "YOUR_GITLAB_TOKEN"
  assignee_username: "your-username"  # Filter issues assigned to you
  auto_process_labels: ["bot", "auto-fix", "ai"]

ai_provider:
  type: "claude"  # or "openai", "ollama", "local"
  api_key: "YOUR_API_KEY"
  model: "claude-sonnet-4-5-20250929"

workspace:
  clone_path: "/tmp/gitissue-ai-agent-workspace"
```

**For GitHub:**

```yaml
github:
  access_token: "YOUR_GITHUB_TOKEN"
  username: "your-username"
  auto_process_labels: ["bot", "auto-fix", "ai"]

ai_provider:
  type: "claude"
  api_key: "YOUR_API_KEY"
  model: "claude-sonnet-4-5-20250929"

workspace:
  clone_path: "/tmp/gitissue-ai-agent-workspace"
```

**Get Tokens:**

GitLab:
1. Visit GitLab > Preferences > Access Tokens
2. Create new token with permissions: `api`, `read_repository`, `write_repository`

GitHub:
1. Visit GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Create new token with scopes: `repo`, `workflow`

#### Run

**API Mode (Standalone)**

```bash
# Run once
python main.py

# Or use the helper script
./run.sh

# View statistics
python main.py --stats

# Schedule with cron (every hour)
0 * * * * cd /path/to/gitissue-ai-agent && ./run.sh
```

**MCP Mode (Claude Code Integration)**

```bash
# 1. Setup MCP server
./setup_mcp.sh

# 2. Restart Claude Code

# 3. Talk to Claude:
"帮我检查并处理 GitLab issues"
```

See [MCP Setup Guide](docs/MCP_SETUP.md) for details.

<a name="try-it-on-this-repo"></a>

### 🐙 Try It on This Repository!

Want to see the agent in action? Try it on this repository!

1. **Create an issue** in this repository: https://github.com/submato/gitissue-ai-agent/issues/new
2. **Add labels**: Add `bot` label to trigger automation
3. **Describe your request**:
   - Bug fixes: "Fix typo in README"
   - Features: "Add Docker support"
   - Documentation: "Improve installation guide"
4. **Watch the agent work**: The agent will:
   - Analyze your issue
   - Comment if more info needed
   - Create PR with fix
   - Update labels automatically

**Example Issues You Can Create:**

- `[bot]` Fix typo in documentation
- `[bot] [urgent]` Add example configuration file
- `[bot]` Improve error handling in main.py

The agent is configured to help maintain this repository!

### 📋 Complete Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    Issue Created (Manual)                     │
│              User creates issue on GitLab/GitHub              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      Agent Detection                          │
│   • Checks for trigger labels (bot, auto-fix, ai)           │
│   • Filters assigned issues                                  │
│   • Skips already processed issues                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      AI Analysis Phase                        │
│   Claude/GPT-4 analyzes:                                     │
│   • Issue description and context                            │
│   • Code repository structure                                │
│   • Feasibility assessment                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │   Need More     │   │   Can Handle    │
    │   Information   │   │                 │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ Post Comment    │   │   Clone Repo    │
    │ @mention author │   │   Create Branch │
    │ Ask questions   │   │                 │
    │ Add label:      │   └────────┬────────┘
    │ "needs-info"    │            │
    └────────┬────────┘            ▼
             │           ┌─────────────────┐
             │           │  Implement Fix  │
             │           │  Run Tests      │
             │           │  Verify Changes │
             │           └────────┬────────┘
             │                    │
             │                    ▼
             │           ┌─────────────────┐
             │           │   Commit Code   │
             │           │   Push Branch   │
             │           └────────┬────────┘
             │                    │
             │                    ▼
             │           ┌─────────────────┐
             │           │  Create MR/PR   │
             │           │  Link to Issue  │
             │           │  Add label:     │
             │           │  "ready-review" │
             │           └────────┬────────┘
             │                    │
             └────────────────────┼─────────────────────┐
                                  ▼                     │
                         ┌─────────────────┐            │
                         │ Post Comment    │            │
                         │ on Issue        │            │
                         │ • MR/PR link    │            │
                         │ • Summary       │            │
                         └────────┬────────┘            │
                                  │                     │
                                  ▼                     ▼
                         ┌─────────────────┐   ┌────────────────┐
                         │ Update State    │   │ Wait for Reply │
                         │ Mark Complete   │   │ Re-analyze     │
                         └─────────────────┘   └────────────────┘
```

### 🎬 Example Workflow Scenarios

#### Scenario 1: Auto-fixable Bug

```
1. User creates issue: "Fix login button CSS on mobile"
   Labels: [bot, bug]

2. Agent detects and analyzes
   → Decision: can_handle

3. Agent actions:
   ✓ Clone repository
   ✓ Create branch: bot/issue-123-fix-login-button
   ✓ Fix CSS in styles/login.css
   ✓ Run tests
   ✓ Commit: "Fix #123: Fix login button CSS on mobile"
   ✓ Push and create MR
   ✓ Add label: ready-review
   ✓ Comment on issue with MR link

4. Result: Issue linked to MR, ready for human review
```

#### Scenario 2: Need More Information

```
1. User creates issue: "Add export feature"
   Labels: [bot, feature]

2. Agent detects and analyzes
   → Decision: need_info

3. Agent actions:
   ✓ Post comment:
     "@author I need more information:
      1. What data to export?
      2. Export format (CSV/JSON/Excel)?
      3. Any filters needed?"
   ✓ Add label: needs-info

4. User replies with details

5. Agent re-analyzes
   → Decision: can_handle
   → Proceeds with implementation

6. Result: Feature implemented with proper requirements
```

### 🎯 Two Execution Modes

| Feature | API Mode | MCP Mode |
|---------|----------|----------|
| Direct code execution | ❌ | ✅ |
| Human intervention needed | ✅ | ❌ |
| Deploy to server | ✅ | ❌ |
| Real-time processing | ❌ | ✅ |
| Full project context | ❌ | ✅ |
| Auto create MR | Manual | ✅ Auto |

**Recommendation**: Use MCP mode for local development, API mode for production deployment.

### 🏷️ Label System & Management

#### Trigger Labels (Start Processing)

These labels tell the agent to process an issue:

- `bot` - General automation tasks
- `auto-fix` - Auto-fixable bugs
- `ai` - AI-assisted features
- `urgent` - High priority (process first)

#### Status Labels (Auto-managed by Agent)

The agent automatically adds/updates these labels during processing:

- `analyzing` - Agent is analyzing the issue
- `needs-info` - Waiting for more information from author
- `in-progress` - Agent is working on the fix
- `ready-review` - MR/PR created, ready for human review
- `completed` - Issue resolved and merged
- `cannot-fix` - Issue too complex for automated handling
- `blocked` - Blocked by external dependencies

#### Priority Labels

- `urgent` - Process immediately (highest priority)
- `high` - Process soon
- `normal` - Standard priority (default)
- `low` - Process when idle

#### Agent Capabilities

The agent can intelligently:

✅ **Add labels** based on analysis results
✅ **Update labels** as status changes
✅ **Read labels** to determine priority
✅ **Remove labels** when no longer applicable
✅ **Preserve user labels** (doesn't remove manual labels)

#### Label-based Filtering

Configure which labels trigger automation in `config.yaml`:

```yaml
gitlab:
  auto_process_labels: ["bot", "auto-fix", "ai"]
  priority_labels:
    urgent: 10
    high: 5
    normal: 1
    low: 0
```

### 📊 Project Structure

```
gitissue-ai-agent/
├── core/                       # Core functionality
│   ├── gitlab.py              # GitLab API client
│   ├── agent.py               # Issue processing agent
│   └── state.py               # State management
│
├── providers/                  # AI Provider plugins
│   ├── base.py                # Base interface
│   ├── claude.py              # Claude API Provider
│   └── mcp.py                 # MCP Provider
│
├── config/                     # Configuration
│   ├── config.yaml            # Your config (gitignored)
│   └── config.example.yaml    # Config template
│
├── docs/                       # Documentation
│   └── MCP_SETUP.md           # MCP setup guide
│
├── main.py                     # API mode entry point
├── mcp_server.py              # MCP Server
├── manage.py                  # Management CLI
├── process_issue.py           # Process specific issue
├── run.sh                      # Quick start script
└── setup_mcp.sh               # MCP auto-config script
```

### 🔧 Management Tools

```bash
# List all issues
python manage.py list

# Show statistics
python manage.py stats

# View configuration
python manage.py config

# Reset state
python manage.py reset

# Process specific issue
python process_issue.py group/project#123

# Test all components
python test_components.py
```

### 🔒 Security

- ⚠️ Never commit `config.yaml` with tokens
- 🔑 Use environment variables for sensitive data
- 👤 Create dedicated GitLab bot account
- 🔐 Minimal token permissions (api, read_repository, write_repository)

### 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

### 📝 License

MIT License - see [LICENSE](LICENSE)

### 🙏 Acknowledgments

- Anthropic Claude for AI capabilities
- GitLab for the excellent API
- Open source community

---

<a name="chinese"></a>

## 中文

> 🎯 **本仓库已接入 Agent！** 想体验效果？[创建一个带 `bot` 标签的 issue](#try-it-on-this-repo-zh) 看 AI agent 自动处理！

> 使用 AI 自动解决 GitLab issues - 首个智能 GitLab issue 自动化框架

---

## 🚀 立即体验！

**本仓库已启用 agent！** 亲身体验 AI 驱动的 issue 自动化处理：

👉 **[快速测试：创建 Issue](#try-it-on-this-repo-zh)** - 观看 agent 自动分析、评论并创建 PR！

---

### 🌟 特性

- 🤖 **自动解决 Issue** - AI 自动分析并解决 GitLab/GitHub issues
- 💬 **智能评论** - 需要时通过 @mention 向 issue 作者询问
- 🔧 **自动创建 MR/PR** - 自动创建包含修复的合并/拉取请求
- 📊 **多平台支持** - 处理 GitLab 和 GitHub 的 issues
- 📁 **多项目支持** - 处理所有项目中的 issues
- 🔌 **可插拔 AI** - 支持 Claude、GPT-4、本地 LLM 等
- 🏷️ **标签驱动** - 通过 issue 标签控制自动化（自动管理）
- 📈 **状态管理** - 永不重复处理同一个 issue
- ⚡ **双模式** - API 模式用于服务器，MCP 模式集成 Claude Code

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/gitissue-ai-agent.git
cd gitissue-ai-agent

# 安装依赖
pip install -r requirements.txt

# 复制配置模板
cp config/config.example.yaml config/config.yaml
```

#### 配置

编辑 `config/config.yaml`:

```yaml
gitlab:
  url: "https://gitlab.com"
  access_token: "你的_GITLAB_TOKEN"
  assignee_username: "你的用户名"
  auto_process_labels: ["bot", "auto-fix", "ai"]

ai_provider:
  type: "claude"  # 或 "openai", "ollama", "local"
  api_key: "你的_API_KEY"
  model: "claude-sonnet-4-5-20250929"

workspace:
  clone_path: "/tmp/gitissue-ai-agent-workspace"
```

**获取 GitLab Token:**
1. 访问 GitLab > Preferences > Access Tokens
2. 创建新 token，权限：`api`, `read_repository`, `write_repository`

#### 运行

**API 模式（独立运行）**

```bash
# 运行一次
python main.py

# 或使用快捷脚本
./run.sh

# 查看统计
python main.py --stats

# 定时运行（每小时）
0 * * * * cd /path/to/gitissue-ai-agent && ./run.sh
```

**MCP 模式（Claude Code 集成）**

```bash
# 1. 设置 MCP server
./setup_mcp.sh

# 2. 重启 Claude Code

# 3. 对 Claude 说：
"帮我检查并处理 GitLab issues"
```

详见 [MCP 设置指南](docs/MCP_SETUP.md)。

<a name="try-it-on-this-repo-zh"></a>

### 🐙 在本仓库体验！

想看看 agent 的实际效果？在本仓库上试试吧！

1. **创建 issue**：https://github.com/submato/gitissue-ai-agent/issues/new
2. **添加标签**：添加 `bot` 标签触发自动化
3. **描述你的需求**：
   - Bug 修复："修复 README 中的错别字"
   - 新功能："添加 Docker 支持"
   - 文档改进："改进安装指南"
4. **观察 agent 工作**：agent 会：
   - 分析你的 issue
   - 需要时评论询问
   - 创建 PR 修复
   - 自动更新标签

**示例 Issues：**

- `[bot]` 修复文档中的错别字
- `[bot] [urgent]` 添加示例配置文件
- `[bot]` 改进 main.py 的错误处理

Agent 已配置好帮助维护本仓库！

### 📋 完整工作流程

```
┌──────────────────────────────────────────────────────────────┐
│                    创建 Issue（人工）                         │
│              用户在 GitLab/GitHub 创建 issue                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      Agent 检测                               │
│   • 检查触发标签 (bot, auto-fix, ai)                        │
│   • 过滤已分配的 issues                                      │
│   • 跳过已处理的 issues                                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      AI 分析阶段                              │
│   Claude/GPT-4 分析：                                        │
│   • Issue 描述和上下文                                       │
│   • 代码仓库结构                                             │
│   • 可行性评估                                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │   需要更多      │   │   可以处理      │
    │   信息          │   │                 │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │ 发布评论        │   │   克隆仓库      │
    │ @mention 作者   │   │   创建分支      │
    │ 询问问题        │   │                 │
    │ 添加标签：      │   └────────┬────────┘
    │ "needs-info"    │            │
    └────────┬────────┘            ▼
             │           ┌─────────────────┐
             │           │  实现修复       │
             │           │  运行测试       │
             │           │  验证更改       │
             │           └────────┬────────┘
             │                    │
             │                    ▼
             │           ┌─────────────────┐
             │           │   提交代码      │
             │           │   推送分支      │
             │           └────────┬────────┘
             │                    │
             │                    ▼
             │           ┌─────────────────┐
             │           │  创建 MR/PR     │
             │           │  链接到 Issue   │
             │           │  添加标签：     │
             │           │  "ready-review" │
             │           └────────┬────────┘
             │                    │
             └────────────────────┼─────────────────────┐
                                  ▼                     │
                         ┌─────────────────┐            │
                         │ 在 Issue 评论   │            │
                         │ • MR/PR 链接    │            │
                         │ • 摘要说明      │            │
                         └────────┬────────┘            │
                                  │                     │
                                  ▼                     ▼
                         ┌─────────────────┐   ┌────────────────┐
                         │ 更新状态        │   │ 等待回复       │
                         │ 标记完成        │   │ 重新分析       │
                         └─────────────────┘   └────────────────┘
```

### 🏷️ 标签系统与管理

#### 触发标签（启动处理）

这些标签告诉 agent 处理 issue：

- `bot` - 通用自动化任务
- `auto-fix` - 可自动修复的 bug
- `ai` - AI 辅助功能
- `urgent` - 高优先级（优先处理）

#### 状态标签（Agent 自动管理）

Agent 在处理过程中自动添加/更新这些标签：

- `analyzing` - Agent 正在分析 issue
- `needs-info` - 等待作者提供更多信息
- `in-progress` - Agent 正在处理修复
- `ready-review` - MR/PR 已创建，等待人工审核
- `completed` - Issue 已解决并合并
- `cannot-fix` - Issue 过于复杂，无法自动处理
- `blocked` - 被外部依赖阻塞

#### 优先级标签

- `urgent` - 立即处理（最高优先级）
- `high` - 尽快处理
- `normal` - 标准优先级（默认）
- `low` - 空闲时处理

#### Agent 能力

Agent 可以智能地：

✅ **添加标签** - 基于分析结果
✅ **更新标签** - 随状态变化
✅ **读取标签** - 确定优先级
✅ **删除标签** - 当不再适用时
✅ **保留用户标签** - 不删除手动标签

### 🎯 两种执行模式

| 特性 | API 模式 | MCP 模式 |
|------|---------|----------|
| 直接执行代码 | ❌ | ✅ |
| 需要人工干预 | ✅ | ❌ |
| 部署到服务器 | ✅ | ❌ |
| 实时处理 | ❌ | ✅ |
| 完整项目上下文 | ❌ | ✅ |
| 自动创建 MR | 手动 | ✅ 自动 |

**建议**: 本地开发用 MCP 模式，生产部署用 API 模式。

### 🔧 管理工具

```bash
# 列出所有 issues
python manage.py list

# 显示统计
python manage.py stats

# 查看配置
python manage.py config

# 重置状态
python manage.py reset

# 处理特定 issue
python process_issue.py group/project#123

# 测试所有组件
python test_components.py
```

### 🔒 安全

- ⚠️ 永远不要提交包含 token 的 `config.yaml`
- 🔑 使用环境变量存储敏感数据
- 👤 创建专用的 GitLab 机器人账号
- 🔐 最小权限原则（api, read_repository, write_repository）

### 🤝 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md)

### 📝 许可证

MIT License - 查看 [LICENSE](LICENSE)

### 🙏 致谢

- Anthropic Claude 提供 AI 能力
- GitLab 提供优秀的 API
- 开源社区

---

**Made with ❤️ by developers, for developers**

⭐ If you find this project useful, please give it a star!
