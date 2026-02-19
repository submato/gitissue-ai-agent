#!/bin/bash
# 自动配置 MCP Server 到 Claude Code

set -e

echo "🔧 GitLab AI Agent - MCP Server 配置工具"
echo "========================================"
echo ""

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_SERVER_PATH="$PROJECT_DIR/mcp_server.py"

# Claude Code 配置目录
CLAUDE_CONFIG_DIR="$HOME/.claude"
CLAUDE_MCP_FILE="$CLAUDE_CONFIG_DIR/mcp_servers.json"

# 检查 Claude Code 配置目录
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "❌ 未找到 Claude Code 配置目录: $CLAUDE_CONFIG_DIR"
    echo "💡 请确保已安装 Claude Code"
    exit 1
fi

echo "✅ 找到 Claude Code 配置目录: $CLAUDE_CONFIG_DIR"

# 创建或更新 MCP 配置
if [ -f "$CLAUDE_MCP_FILE" ]; then
    echo "📝 已存在 MCP 配置文件，将添加 gitissue-ai-agent"
    # 备份现有配置
    cp "$CLAUDE_MCP_FILE" "$CLAUDE_MCP_FILE.backup.$(date +%s)"
    echo "💾 已备份到: $CLAUDE_MCP_FILE.backup.*"

    # 使用 Python 合并配置
    python3 << EOF
import json

with open('$CLAUDE_MCP_FILE', 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['gitissue-ai-agent'] = {
    'command': 'python3',
    'args': ['$MCP_SERVER_PATH']
}

with open('$CLAUDE_MCP_FILE', 'w') as f:
    json.dump(config, f, indent=2)

print('✅ 配置已更新')
EOF

else
    echo "📝 创建新的 MCP 配置文件"
    cat > "$CLAUDE_MCP_FILE" << EOF
{
  "mcpServers": {
    "gitissue-ai-agent": {
      "command": "python3",
      "args": ["$MCP_SERVER_PATH"]
    }
  }
}
EOF
    echo "✅ 配置文件已创建: $CLAUDE_MCP_FILE"
fi

echo ""
echo "🎉 MCP Server 配置完成！"
echo ""
echo "📋 下一步："
echo "  1. 重启 Claude Code"
echo "  2. 在 Claude Code 中对我说："
echo "     \"帮我检查 GitLab issues\""
echo ""
echo "  3. 我会自动调用 MCP tools 来处理 issues！"
echo ""
echo "📚 详细文档: docs/MCP_SETUP.md"
echo ""
