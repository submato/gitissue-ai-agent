# 多项目监听配置指南

本项目支持同时监听多个 GitHub 和 GitLab 项目的 issues。

## 📋 配置方式对比

### GitHub 项目（环境变量配置）

**监听单个项目：**

编辑 `run_auto_process.sh`：
```bash
export REPO_OWNER="submato"              # 仓库所有者
export REPO_NAME="gitissue-ai-agent"     # 仓库名称
```

**监听多个项目：**

创建多个脚本，每个监听一个项目：

`run_auto_process_project1.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
export USE_LOCAL_PROXY=1
export GITHUB_TOKEN="${GITHUB_TOKEN}"
export REPO_OWNER="user1"
export REPO_NAME="project1"
export ANTHROPIC_API_KEY="any_value"
python3 auto_process_issues.py
```

`run_auto_process_project2.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
export USE_LOCAL_PROXY=1
export GITHUB_TOKEN="${GITHUB_TOKEN}"
export REPO_OWNER="user2"
export REPO_NAME="project2"
export ANTHROPIC_API_KEY="any_value"
python3 auto_process_issues.py
```

然后在 crontab 中添加多个任务：
```bash
crontab -e

# 项目 1 - 每 3 分钟
*/3 * * * * export GITHUB_TOKEN='your_token' && /path/to/run_auto_process_project1.sh >> /path/to/logs/project1.log 2>&1

# 项目 2 - 每 3 分钟
*/3 * * * * export GITHUB_TOKEN='your_token' && /path/to/run_auto_process_project2.sh >> /path/to/logs/project2.log 2>&1
```

---

### GitLab 项目（配置文件）

**监听单个项目：**

GitLab 通过 `config/config.yaml` 配置：

```yaml
gitlab:
  url: "https://gitlab.com"
  access_token: "YOUR_GITLAB_TOKEN"
  assignee_username: "your-username"  # 只处理分配给此用户的 issues
  auto_process_labels:
    - "bot"
    - "auto-fix"
    - "ai"

ai_provider:
  type: "claude"
  claude:
    api_key: "YOUR_API_KEY"
    api_base: "http://localhost:8082"  # 可选：本地代理
    model: "claude-sonnet-4-5-20250929"

state_file: "state.json"
```

**监听多个 GitLab 项目：**

创建多个配置文件：

`config/config_project1.yaml`:
```yaml
gitlab:
  url: "https://gitlab.com"
  access_token: "YOUR_GITLAB_TOKEN"
  assignee_username: "your-username"
  auto_process_labels: ["bot"]

ai_provider:
  type: "claude"
  claude:
    api_key: "YOUR_API_KEY"
    api_base: "http://localhost:8082"
    model: "claude-sonnet-4-5-20250929"

state_file: "state_project1.json"  # 每个项目单独的状态文件
```

`config/config_project2.yaml`:
```yaml
gitlab:
  url: "https://gitlab.example.com"  # 可以是不同的 GitLab 实例
  access_token: "YOUR_GITLAB_TOKEN_2"
  assignee_username: "your-username"
  auto_process_labels: ["bot"]

ai_provider:
  type: "claude"
  claude:
    api_key: "YOUR_API_KEY"
    api_base: "http://localhost:8082"
    model: "claude-sonnet-4-5-20250929"

state_file: "state_project2.json"
```

然后在 crontab 中添加：
```bash
crontab -e

# GitLab 项目 1 - 每 5 分钟
*/5 * * * * export USE_LOCAL_PROXY=1 GITLAB_CONFIG_FILE="/path/to/config/config_project1.yaml" && /path/to/run_gitlab_auto_process.sh >> /path/to/logs/gitlab_project1.log 2>&1

# GitLab 项目 2 - 每 5 分钟
*/5 * * * * export USE_LOCAL_PROXY=1 GITLAB_CONFIG_FILE="/path/to/config/config_project2.yaml" && /path/to/run_gitlab_auto_process.sh >> /path/to/logs/gitlab_project2.log 2>&1
```

---

## 🔧 GitLab 特殊配置说明

### 1. `assignee_username` - 过滤用户

GitLab 使用 `assignee_username` 字段来**只处理分配给特定用户的 issues**：

```yaml
assignee_username: "your-username"  # 只处理分配给 your-username 的 issues
```

如果想处理**所有带标签的 issues**（不管分配给谁）：
- 可以省略 `assignee_username` 字段
- 或者修改 `core/agent.py` 中的过滤逻辑

### 2. `auto_process_labels` - 触发标签

只有带这些标签的 issues 才会被自动处理：

```yaml
auto_process_labels:
  - "bot"        # 带 bot 标签
  - "auto-fix"   # 或 auto-fix 标签
  - "ai"         # 或 ai 标签
```

### 3. GitLab vs GitHub 的区别

| 特性 | GitHub | GitLab |
|------|--------|--------|
| 配置方式 | 环境变量 | config.yaml |
| 项目指定 | REPO_OWNER + REPO_NAME | 通过 assignee_username 过滤 |
| 标签过滤 | 固定 'bot' | 可配置多个标签 |
| 多项目 | 多个脚本 | 多个配置文件 |
| 状态管理 | processed_issues.json | state.json |

---

## 🎯 推荐配置

### 单一 GitHub 项目（当前配置）

```bash
# 已配置：submato/gitissue-ai-agent
# Cron: 每 3 分钟
*/3 * * * * export GITHUB_TOKEN='...' && /home/mhyuser/gitissue-ai-agent/run_auto_process.sh
```

### 添加 GitLab 项目

1. 创建配置文件：`config/config.yaml`（参考 config.example.yaml）
2. 填写 GitLab 信息和 token
3. 添加 cron 任务：
   ```bash
   */5 * * * * export USE_LOCAL_PROXY=1 && /home/mhyuser/gitissue-ai-agent/run_gitlab_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/gitlab_cron.log 2>&1
   ```

### 同时监听多个项目

```bash
# GitHub 项目 1 (submato/gitissue-ai-agent) - 每 3 分钟
*/3 * * * * export GITHUB_TOKEN='...' REPO_OWNER='submato' REPO_NAME='gitissue-ai-agent' && /home/mhyuser/gitissue-ai-agent/run_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/github1.log 2>&1

# GitHub 项目 2 (user/other-repo) - 每 5 分钟
*/5 * * * * export GITHUB_TOKEN='...' REPO_OWNER='user' REPO_NAME='other-repo' && /home/mhyuser/gitissue-ai-agent/run_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/github2.log 2>&1

# GitLab 项目 - 每 5 分钟
*/5 * * * * export USE_LOCAL_PROXY=1 && /home/mhyuser/gitissue-ai-agent/run_gitlab_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/gitlab.log 2>&1
```

---

## 📝 常见问题

**Q: GitHub 可以像 GitLab 一样用配置文件吗？**

A: 可以！修改 `auto_process_issues.py`，从配置文件读取而不是环境变量。

**Q: GitLab 可以监听多个项目的 issues 吗？**

A: GitLab 的逻辑是通过 `assignee_username` 过滤，会获取**所有分配给该用户的 issues**，不限项目。如果只想监听特定项目，需要修改 `core/agent.py`。

**Q: 如何监听所有 GitLab issues（不按 assignee 过滤）？**

A: 修改 `core/agent.py` 中的 `process_all_issues` 方法，移除 `assignee` 参数。

**Q: 日志在哪里？**

A:
- GitHub: `logs/auto_process.log` 和 `logs/cron.log`
- GitLab: `logs/gitlab_auto_process.log` 和自定义 cron 日志

---

## 🚀 快速示例

**监听你自己的 GitHub 项目：**

```bash
# 1. 编辑环境变量
export REPO_OWNER="your-username"
export REPO_NAME="your-repo"

# 2. 运行测试
./run_auto_process.sh

# 3. 添加到 cron
crontab -e
# 添加：
*/3 * * * * export GITHUB_TOKEN='your_token' REPO_OWNER='your-username' REPO_NAME='your-repo' && /home/mhyuser/gitissue-ai-agent/run_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/my_project.log 2>&1
```

**监听 GitLab 项目：**

```bash
# 1. 创建配置
cp config/config.example.yaml config/config.yaml
nano config/config.yaml  # 填写你的 GitLab 信息

# 2. 测试
./run_gitlab_auto_process.sh

# 3. 添加到 cron
crontab -e
# 添加：
*/5 * * * * export USE_LOCAL_PROXY=1 && /home/mhyuser/gitissue-ai-agent/run_gitlab_auto_process.sh >> /home/mhyuser/gitissue-ai-agent/logs/gitlab.log 2>&1
```

搞定！🎉
