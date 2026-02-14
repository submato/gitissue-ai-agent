# 快速开始指南

## 1. 安装

```bash
git clone https://github.com/YOUR_USERNAME/gitlab-ai-agent.git
cd gitlab-ai-agent
pip install -r requirements.txt
```

## 2. 配置

复制配置模板：
```bash
cp config/config.example.yaml config/config.yaml
```

编辑 `config/config.yaml`：

```yaml
gitlab:
  url: "https://your-gitlab.com"
  access_token: "YOUR_TOKEN"  # GitLab Personal Access Token
  assignee_username: "your-username"
  auto_process_labels:
    - "bot"
    - "auto-fix"

ai_provider:
  type: "claude"
  claude:
    api_key: "YOUR_CLAUDE_API_KEY"
    model: "claude-sonnet-4-5-20250929"
```

### 获取 GitLab Token

1. 访问 GitLab > Preferences > Access Tokens
2. 创建新 token
3. 权限：`api`, `read_repository`, `write_repository`

### 获取 Claude API Key

访问 https://console.anthropic.com/settings/keys

## 3. 运行

### 手动运行

```bash
python3 main.py
```

或使用快捷脚本：

```bash
./run.sh
```

### 查看统计

```bash
python3 main.py --stats
```

### 定时运行（crontab）

```bash
# 编辑 crontab
crontab -e

# 每小时运行
0 * * * * cd /path/to/gitlab-ai-agent && ./run.sh >> logs/cron.log 2>&1
```

## 4. 使用

### 在 GitLab Issue 上添加标签

给需要 AI 处理的 issue 添加标签：
- `bot` - 通用任务
- `auto-fix` - 自动修复
- `ai` - AI 辅助

### Agent 工作流程

1. **拉取 issues** - 获取分配给你的带标签的 issues
2. **AI 分析** - Claude 分析 issue 内容
3. **决策执行**：
   - **can_handle** - 生成修复计划
   - **need_info** - 在 issue 评论询问
   - **skip** - 跳过不适合的 issue

## 5. 示例

### 示例 1：Bug 修复

**Issue:**
```
标签: auto-fix
标题: 修复登录按钮样式
描述: 登录按钮在手机端显示不正确
```

**Agent 行为:**
1. 分析 issue，确定可以处理
2. 生成修复计划（调整 CSS）
3. 输出详细的修复指令
4. （可选）自动执行并创建 MR

### 示例 2：需要更多信息

**Issue:**
```
标签: bot
标题: 添加导出功能
描述: 需要导出数据
```

**Agent 行为:**
1. 分析发现信息不足
2. 在 issue 评论：
   ```
   @author 你好！我需要更多信息：
   1. 导出什么数据？
   2. 导出格式？（CSV/JSON/Excel）
   3. 是否需要筛选？
   ```

## 6. 故障排除

### GitLab API 401 错误
- 检查 token 是否正确
- 确认 token 权限

### AI 分析失败
- 检查 API key
- 确认网络连接
- 查看日志：`tail -f gitlab-agent.log`

### 找不到 issues
- 确认 issue 有正确的标签
- 确认 issue 分配给了配置的用户
- 检查 `state.json`，可能已处理

## 7. 高级配置

### 使用本地 AI 代理

```yaml
ai_provider:
  type: "claude"
  claude:
    api_base: "http://localhost:8082"
    api_key: "any-value"
```

### 多项目配置

在 `config.yaml` 中添加项目列表（未来功能）

### 自定义提示词

修改 `providers/claude.py` 中的 `_build_analysis_prompt` 方法

## 8. 下一步

- 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献
- 加入我们的社区讨论
- Star ⭐ 这个项目！

## 需要帮助？

- 📖 查看完整文档：[README.md](README.md)
- 🐛 报告问题：[GitHub Issues](https://github.com/YOUR_USERNAME/gitlab-ai-agent/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/YOUR_USERNAME/gitlab-ai-agent/discussions)
