# GitHub vs GitLab 配置完整指南

## 🎯 核心区别

### GitHub（仓库维度）🐙
**监听模式：** 明确指定要监听哪些仓库

**适合场景：**
- ✅ 个人项目（你是 owner）
- ✅ 开源项目（你是 contributor）
- ✅ 你关心的特定仓库
- ✅ 自己选择监听范围

**配置方式：**
```bash
# 单个仓库
export REPO_OWNER="submato"
export REPO_NAME="gitissue-ai-agent"
./run_auto_process.sh

# 多个仓库（推荐）
export GITHUB_REPOS="submato/gitissue-ai-agent,user/project1,org/project2"
./run_github_multi_repos.sh
```

---

### GitLab（用户维度）🦊
**监听模式：** 自动监听所有分配给你的 issues（跨所有项目）

**适合场景：**
- ✅ 公司/企业环境
- ✅ 团队协作项目
- ✅ 你被分配了很多 issues
- ✅ 不想逐个配置每个项目

**配置方式：**
```yaml
# config/config.yaml
gitlab:
  url: "https://gitlab.com"
  access_token: "YOUR_TOKEN"
  assignee_username: "your-username"  # 关键：监听所有分配给此用户的 issues
  auto_process_labels: ["bot"]
```

---

## 📊 对比表格

| 特性 | GitHub | GitLab |
|------|--------|--------|
| **监听范围** | 指定的仓库 | 分配给用户的所有 issues |
| **配置方式** | 环境变量 | YAML 配置文件 |
| **项目数量** | 显式列出 | 自动包含所有 |
| **过滤方式** | owner/repo | assignee_username |
| **使用场景** | 个人/开源 | 企业/团队 |
| **心智模型** | "监听这些仓库" | "监听我的工作" |

---

## 🚀 快速开始

### GitHub 单仓库

```bash
# 1. 设置要监听的仓库
export GITHUB_TOKEN="your_token"
export REPO_OWNER="your-username"
export REPO_NAME="your-repo"

# 2. 运行
./run_auto_process.sh

# 3. 添加到 cron（每 3 分钟）
crontab -e
*/3 * * * * export GITHUB_TOKEN='token' REPO_OWNER='user' REPO_NAME='repo' && /path/to/run_auto_process.sh >> /path/to/logs/cron.log 2>&1
```

### GitHub 多仓库（推荐）

```bash
# 1. 设置仓库列表
export GITHUB_TOKEN="your_token"
export GITHUB_REPOS="user1/repo1,user2/repo2,org/repo3"

# 2. 运行
./run_github_multi_repos.sh

# 3. 添加到 cron
crontab -e
*/3 * * * * export GITHUB_TOKEN='token' GITHUB_REPOS='repo1,repo2' && /path/to/run_github_multi_repos.sh >> /path/to/logs/cron.log 2>&1
```

### GitLab（所有你的 issues）

```bash
# 1. 创建配置文件
cp config/config.example.yaml config/config.yaml

# 2. 编辑配置
nano config/config.yaml
# 填写：
#   - access_token: 你的 GitLab token
#   - assignee_username: 你的 GitLab 用户名

# 3. 运行
./run_gitlab_auto_process.sh

# 4. 添加到 cron
crontab -e
*/5 * * * * export USE_LOCAL_PROXY=1 && /path/to/run_gitlab_auto_process.sh >> /path/to/logs/gitlab_cron.log 2>&1
```

---

## 💡 实际使用示例

### 个人开发者（GitHub）

**场景：** 小明有 3 个开源项目和 2 个个人项目想用 AI 处理 issues

```bash
# 一次性监听 5 个项目
export GITHUB_REPOS="xiaoming/awesome-lib,xiaoming/cool-app,xiaoming/my-blog,org/shared-tool,team/common-utils"
./run_github_multi_repos.sh
```

✅ **优点：** 明确知道监听哪些项目，控制精准

---

### 公司程序员（GitLab）

**场景：** 小红在公司参与 10+ 个项目，每天被分配各种 issues

```yaml
# config/config.yaml
gitlab:
  assignee_username: "xiaohong"
```

✅ **优点：** 无论在哪个项目被分配 issue，agent 都会自动处理，不需要配置每个项目

---

## 🔧 高级配置

### 监听不同组织的仓库

```bash
# GitHub 支持跨组织
export GITHUB_REPOS="myuser/personal,company-org/project1,opensource-org/tool"
```

### GitLab 多实例

```bash
# 可以运行多个实例
# 实例 1：公司 GitLab
GITLAB_CONFIG_FILE=config/company.yaml ./run_gitlab_auto_process.sh

# 实例 2：GitLab.com
GITLAB_CONFIG_FILE=config/gitlab.com.yaml ./run_gitlab_auto_process.sh
```

### 混合使用

```bash
# Cron 中同时运行 GitHub 和 GitLab

# GitHub 多仓库 - 每 3 分钟
*/3 * * * * export GITHUB_TOKEN='xxx' GITHUB_REPOS='repo1,repo2' && /path/to/run_github_multi_repos.sh >> /path/to/logs/github.log 2>&1

# GitLab 用户 issues - 每 5 分钟
*/5 * * * * export USE_LOCAL_PROXY=1 && /path/to/run_gitlab_auto_process.sh >> /path/to/logs/gitlab.log 2>&1
```

---

## ❓ 常见问题

**Q: GitHub 可以像 GitLab 一样监听"我的所有 issues"吗？**

A: 不行。GitHub API 不提供"获取分配给某用户的所有 issues"的接口。只能按仓库获取。

**Q: GitLab 可以像 GitHub 一样只监听特定项目吗？**

A: 可以！修改 `core/agent.py`，添加项目过滤逻辑。但默认是用户维度，更符合团队场景。

**Q: 我应该选 GitHub 模式还是 GitLab 模式？**

A:
- 如果你知道要监听哪些项目 → GitHub 模式
- 如果你想"监听所有我负责的工作" → GitLab 模式

**Q: 可以同时用两种模式吗？**

A: 完全可以！在 cron 中同时配置，GitHub 处理你的开源项目，GitLab 处理公司项目。

---

## 📝 总结

- **GitHub = 仓库列表**：你明确列出要监听的仓库
  - `user/repo1, user/repo2, org/repo3`

- **GitLab = 用户工作**：系统自动找出分配给你的所有 issues
  - `assignee_username: "your-name"`

选择最适合你工作流的方式！🚀
