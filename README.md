# GitIssue AI Agent 🤖

[English](#english) | [中文](#chinese)

<a name="english"></a>

## English

> Automatically solve GitLab issues with AI - The first intelligent GitLab issue automation framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

### 🌟 Features

- 🤖 **Automatic Issue Resolution** - AI analyzes and solves GitLab issues automatically
- 💬 **Intelligent Comments** - Ask for clarification by @mentioning issue authors when needed
- 🔧 **Auto MR Creation** - Automatically creates merge requests with fixes
- 📊 **Multi-Project Support** - Handle issues across all your GitLab projects
- 🔌 **Pluggable AI Providers** - Support Claude, GPT-4, local LLMs, and more
- 🏷️ **Label-Driven Workflow** - Control automation with issue labels
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

**Get GitLab Token:**
1. Visit GitLab > Preferences > Access Tokens
2. Create new token with permissions: `api`, `read_repository`, `write_repository`

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

### 📋 How It Works

```
┌─────────────────┐
│  GitLab Issues  │  (with labels: bot, auto-fix, ai)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Analysis   │  Claude/GPT-4 analyzes the issue
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
need_info  can_handle
    │         │
    ▼         ▼
 Comment   Fix & MR
 @author   Create
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

### 🏷️ Label System

Control automation with GitLab labels:

- `bot` - General automation tasks
- `auto-fix` - Auto-fixable bugs
- `ai` - AI-assisted features
- `urgent` - High priority (process first)

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

> 使用 AI 自动解决 GitLab issues - 首个智能 GitLab issue 自动化框架

### 🌟 特性

- 🤖 **自动解决 Issue** - AI 自动分析并解决 GitLab issues
- 💬 **智能评论** - 需要时通过 @mention 向 issue 作者询问
- 🔧 **自动创建 MR** - 自动创建包含修复的合并请求
- 📊 **多项目支持** - 处理所有 GitLab 项目中的 issues
- 🔌 **可插拔 AI** - 支持 Claude、GPT-4、本地 LLM 等
- 🏷️ **标签驱动** - 通过 issue 标签控制自动化
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

### 📋 工作原理

```
┌─────────────────┐
│  GitLab Issues  │  (带标签: bot, auto-fix, ai)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI 分析       │  Claude/GPT-4 分析 issue
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
need_info  can_handle
    │         │
    ▼         ▼
 评论询问  修复并创建 MR
 @作者
```

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

### 🏷️ 标签系统

用 GitLab 标签控制自动化：

- `bot` - 通用自动化任务
- `auto-fix` - 可自动修复的 bug
- `ai` - AI 辅助功能
- `urgent` - 高优先级（优先处理）

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
