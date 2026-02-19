# MCP Mode Setup Guide

## 什么是 MCP 模式？

MCP (Model Context Protocol) 模式允许 Claude Code 直接调用 GitLab AI Agent，实现：

- ✅ **我（Claude）直接操作代码** - 无需人工干预
- ✅ **实时处理** - 在 Claude Code 中即时处理 issues
- ✅ **完整上下文** - 我能看到你的整个项目
- ✅ **无 API 成本** - 不需要额外的 API 调用

## 🚀 快速配置

### 1. 将 MCP Server 添加到 Claude Code

编辑你的 Claude Code MCP 配置文件：

**位置**：`~/.claude/config.json` 或项目的 `.claude/config.json`

**添加**：
```json
{
  "mcpServers": {
    "gitissue-ai-agent": {
      "command": "python3",
      "args": [
        "/home/mhyuser/gitissue-ai-agent/mcp_server.py"
      ]
    }
  }
}
```

或者直接复制配置：
```bash
# 如果是全局配置
cp mcp_config.json ~/.claude/mcp_servers.json

# 如果是项目配置
cp mcp_config.json /your/project/.claude/mcp_servers.json
```

### 2. 重启 Claude Code

```bash
# 重启 Claude Code 使配置生效
```

### 3. 验证安装

在 Claude Code 中，我应该能看到以下 MCP 工具：

- `gitlab_fetch_issues` - 获取 issues
- `gitlab_analyze_issue` - 分析 issue
- `gitlab_fix_issue` - 修复 issue
- `gitlab_comment` - 评论 issue

## 📋 使用方式

### 方式 1：直接对话

在 Claude Code 中直接告诉我：

```
"帮我检查 GitLab 上分配给我的 issues"
```

我会自动：
1. 调用 `gitlab_fetch_issues` 获取 issues
2. 分析每个 issue
3. 对于可以处理的，直接修复
4. 对于需要信息的，在 issue 评论询问

### 方式 2：手动触发特定 issue

```
"帮我处理 GitLab issue team/project#123"
```

我会：
1. 获取 issue 详情
2. 分析问题
3. 制定修复计划
4. 直接执行修复
5. 创建 MR
6. 在 issue 中评论

### 方式 3：定期自动处理

设置定时任务：

```bash
# 每小时检查一次
0 * * * * cd /home/mhyuser && claude "检查并处理我的 GitLab issues"
```

## 🎯 MCP 模式 vs API 模式

| 特性 | MCP 模式 | API 模式 |
|------|---------|---------|
| 代码操作 | ✅ 直接操作 | ❌ 生成指令 |
| 人工干预 | ❌ 无需 | ✅ 需要 |
| API 成本 | ✅ 无 | ❌ 有 |
| 运行环境 | Claude Code | 独立/服务器 |
| 上下文 | ✅ 完整 | ❌ 有限 |
| 实时性 | ✅ 实时 | ❌ 定时 |

## 🔧 工作流程示例

### 完整自动化流程

```
你: "帮我处理所有 bot 标签的 issues"

我:
1. 🔍 获取所有带 "bot" 标签的 issues (3个)
2. 📝 分析 issue #123: "修复登录按钮样式"
   - ✅ 可以处理
   - 📋 计划：调整 CSS mobile 样式
3. 🔧 执行修复：
   - git clone ...
   - 创建分支 bot/issue-123-fix
   - 修改 login.css
   - 运行测试 ✅
   - git commit & push
   - 创建 MR !456
   - 在 issue 评论: "@author MR 已创建: !456"
4. ✅ Issue #123 完成！

5. 📝 分析 issue #124: "添加导出功能"
   - ❓ 需要更多信息
   - 在 issue 评论：
     "@author 需要确认：
      1. 导出什么数据？
      2. 格式？CSV/JSON/Excel？"
6. ⏸️  Issue #124 等待反馈

7. 📝 分析 issue #125: "重构整个架构"
   - ⏭️  跳过：不适合自动化

完成！处理了 1 个 issue，询问了 1 个，跳过了 1 个。
```

## 🔐 安全配置

MCP Server 使用你的 GitLab Token，确保：

1. **Token 权限最小化**：
   - ✅ `api`
   - ✅ `read_repository`
   - ✅ `write_repository`
   - ❌ 不需要 admin 权限

2. **配置文件保护**：
   ```bash
   chmod 600 config/config.yaml
   ```

3. **代码审查**：
   - MCP 模式会自动创建 MR
   - 你仍然可以在合并前审查代码

## 🐛 故障排除

### MCP Server 未显示

```bash
# 检查 MCP server 是否可运行
python3 mcp_server.py

# 查看 Claude Code 日志
tail -f ~/.claude/logs/mcp.log
```

### 权限错误

```bash
# 确保脚本可执行
chmod +x mcp_server.py

# 确保依赖已安装
pip install -r requirements.txt
```

### GitLab 连接失败

检查 `config/config.yaml` 中的：
- `gitlab.url` 是否正确
- `gitlab.access_token` 是否有效

## 📚 高级用法

### 自定义 MCP 工具

你可以在 `mcp_server.py` 中添加更多工具：

```python
{
    "name": "gitlab_bulk_close",
    "description": "批量关闭过期 issues",
    "inputSchema": {
        "type": "object",
        "properties": {
            "older_than_days": {
                "type": "integer",
                "description": "多少天前的 issues"
            }
        }
    }
}
```

### 与其他 MCP Servers 结合

GitLab AI Agent 可以与其他 MCP servers 配合：

```json
{
  "mcpServers": {
    "gitissue-ai-agent": {...},
    "github-copilot": {...},
    "slack-notifier": {...}
  }
}
```

## 🎉 开始使用

配置完成后，直接在 Claude Code 中说：

**"帮我检查 GitLab issues"**

我会自动帮你处理！🚀
