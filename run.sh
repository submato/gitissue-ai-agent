#!/bin/bash
# GitLab AI Agent 快速启动脚本

cd "$(dirname "$0")"

echo "🤖 GitLab AI Agent"
echo "=================="
echo ""

# 检查配置文件
if [ ! -f "config/config.yaml" ]; then
    echo "❌ 配置文件不存在"
    echo "💡 请复制 config/config.example.yaml 到 config/config.yaml 并编辑"
    exit 1
fi

# 检查依赖
if ! python3 -c "import anthropic, requests, yaml" 2>/dev/null; then
    echo "📦 安装依赖..."
    pip install -r requirements.txt
fi

# 运行
echo "🚀 启动 Agent..."
echo ""
python3 main.py "$@"
