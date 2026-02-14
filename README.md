# GitLab AI Agent 🤖

> Automatically solve GitLab issues with AI - The first intelligent GitLab issue automation framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Features

- 🤖 **Automatic Issue Resolution** - AI analyzes and solves GitLab issues automatically
- 💬 **Intelligent Comments** - Ask for clarification by @mentioning issue authors when needed
- 🔧 **Auto MR Creation** - Automatically creates merge requests with fixes
- 📊 **Multi-Project Support** - Handle issues across all your GitLab projects
- 🔌 **Pluggable AI Providers** - Support Claude, GPT-4, local LLMs, and more
- 🏷️ **Label-Driven Workflow** - Control automation with issue labels
- 📈 **State Management** - Never process the same issue twice
- 🐳 **Docker Ready** - One-command deployment
- ⚡ **Dual Mode** - API mode for servers, MCP mode for Claude Code integration

## 🚀 Quick Start

### Two Modes Available

**🔹 API Mode** (Standalone) - Run on servers, cron jobs, CI/CD
**🔹 MCP Mode** (Claude Code Integration) - Real-time, direct code manipulation

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gitlab-ai-agent.git
cd gitlab-ai-agent

# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config/config.example.yaml config/config.yaml
```

### Configuration

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
  clone_path: "/tmp/gitlab-ai-agent-workspace"
```

### Run

#### API Mode (Standalone)

```bash
# Run once
python main.py

# Or use the helper script
./run.sh

# Schedule with cron
0 * * * * cd /path/to/gitlab-ai-agent && ./run.sh
```

#### MCP Mode (Claude Code Integration)

```bash
# 1. Configure MCP server in Claude Code
cp mcp_config.json ~/.claude/mcp_servers.json

# 2. Restart Claude Code

# 3. Talk to Claude:
"帮我检查并处理 GitLab issues"
```

See [MCP Setup Guide](docs/MCP_SETUP.md) for details.

## 📋 How It Works

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

### Example Workflow

1. **Issue Created** with label `bot`:
   ```
   Title: Fix login button CSS on mobile
   Description: The login button doesn't display correctly on mobile devices
   ```

2. **AI Analyzes** the issue and determines it can be fixed

3. **Agent Actions**:
   - Clones the repository
   - Identifies the CSS file
   - Fixes the styling issue
   - Runs tests
   - Creates a new branch: `bot/issue-123-fix-login-button`
   - Commits: `Fix #123: Fix login button CSS on mobile`
   - Pushes and creates MR
   - Comments on the issue with MR link

4. **If More Info Needed**:
   ```
   @issue_author Hi! I need more information to fix this:

   1. Which mobile device/browser?
   2. What's the expected behavior?

   🤖 GitLab AI Agent
   ```

## 🎯 Supported AI Providers & Modes

### AI Providers
- ✅ **Claude** (Anthropic) - Best for code
- ✅ **OpenAI** (GPT-4) - General purpose
- 🚧 **Ollama** (Local) - Privacy-first
- 🚧 **Custom** - Bring your own LLM

### Execution Modes

| Feature | API Mode | MCP Mode |
|---------|----------|----------|
| Direct code execution | ❌ | ✅ |
| Human intervention needed | ✅ | ❌ |
| API cost | ✅ | ❌ |
| Deploy to server | ✅ | ❌ |
| Real-time processing | ❌ | ✅ |
| Full project context | ❌ | ✅ |
| Auto create MR | Manual | ✅ Auto |

**Recommendation**: Use MCP mode for local development, API mode for production deployment.

## 🏷️ Label System

Control automation with GitLab labels:

- `bot` - General automation tasks
- `auto-fix` - Auto-fixable bugs
- `ai` - AI-assisted features
- `urgent` - High priority (process first)

## 📊 State Management

Processed issues are tracked in `state.json`:

```json
{
  "project/repo#123": {
    "status": "completed",
    "mr_url": "https://gitlab.com/project/merge_requests/45",
    "processed_at": "2026-02-15T10:30:00Z"
  },
  "project/repo#124": {
    "status": "waiting_for_info",
    "comment": "Asked about requirements"
  }
}
```

## 🐳 Docker Deployment

```bash
docker build -t gitlab-ai-agent .
docker run -v $(pwd)/config:/app/config gitlab-ai-agent
```

Or use docker-compose:

```bash
docker-compose up -d
```

## 🔧 Advanced Configuration

### Multiple Projects

```yaml
gitlab:
  projects:
    - id: "group/project1"
      labels: ["bot"]
    - id: "group/project2"
      labels: ["auto-fix"]
```

### Custom Prompts

```yaml
prompts:
  analysis: "path/to/custom_analysis_prompt.txt"
  fix: "path/to/custom_fix_prompt.txt"
```

### Webhooks (Real-time)

```yaml
webhook:
  enabled: true
  port: 8080
  secret: "YOUR_WEBHOOK_SECRET"
```

## 📈 Monitoring

View statistics:

```bash
python main.py --stats
```

Output:
```
GitLab AI Agent Statistics
==========================
Total Issues Processed: 45
  ✓ Completed: 32
  ⏳ In Progress: 5
  ❓ Waiting for Info: 6
  ✗ Failed: 2

Success Rate: 71%
```

## 🔒 Security

- ⚠️ Never commit `config.yaml` with tokens
- 🔑 Use environment variables for sensitive data
- 👤 Create dedicated GitLab bot account
- 🔐 Minimal token permissions (api, read_repository, write_repository)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Anthropic Claude for AI capabilities
- GitLab for the excellent API

## ⭐ Star History

If you find this project useful, please give it a star!

---

**Made with ❤️ by developers, for developers**
