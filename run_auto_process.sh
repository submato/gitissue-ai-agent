#!/bin/bash
# 自动处理 GitHub issues 的简单脚本
# 定时运行此脚本即可，无需 Flask，无需 Webhook

cd "$(dirname "$0")"

# 设置环境变量
export USE_LOCAL_PROXY=1
export GITHUB_TOKEN="${GITHUB_TOKEN}"  # 从环境变量读取，或者在这里填写你的token
export REPO_OWNER="submato"
export REPO_NAME="gitissue-ai-agent"
export ANTHROPIC_API_KEY="any_value"

# 运行处理脚本
python3 auto_process_issues.py
