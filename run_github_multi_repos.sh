#!/bin/bash
# GitHub 多仓库自动处理脚本
# 一次性处理多个 GitHub 仓库的 issues

cd "$(dirname "$0")"

# 设置环境变量
export USE_LOCAL_PROXY=1
export GITHUB_TOKEN="${GITHUB_TOKEN}"  # 从环境变量读取
export ANTHROPIC_API_KEY="any_value"

# 设置要监听的仓库列表（逗号分隔）
# 格式：owner1/repo1,owner2/repo2,owner3/repo3
export GITHUB_REPOS="${GITHUB_REPOS:-submato/gitissue-ai-agent}"

# 运行处理脚本
python3 auto_process_github_multi_repos.py
