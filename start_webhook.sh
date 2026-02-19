#!/bin/bash
# 启动 GitHub Webhook 服务器

# 设置环境变量
export USE_LOCAL_PROXY=1
export WEBHOOK_PORT=8080
export REPO_OWNER="submato"
export REPO_NAME="gitissue-ai-agent"

# 可选：设置 webhook secret（建议设置以提高安全性）
# export GITHUB_WEBHOOK_SECRET="your_secret_here"

# 启动服务器
echo "Starting GitHub Webhook Server..."
echo "Webhook URL: http://$(hostname -I | awk '{print $1}'):${WEBHOOK_PORT}/webhook"
echo ""
echo "Configure this URL in GitHub:"
echo "  Repository → Settings → Webhooks → Add webhook"
echo ""

python3 webhook_server.py
