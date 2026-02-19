#!/bin/bash
# GitLab 自动处理脚本
# 定时运行此脚本即可

cd "$(dirname "$0")"

# 设置环境变量（可选）
export USE_LOCAL_PROXY=1  # 使用本地 AI 代理
# export GITLAB_CONFIG_FILE="config/config.yaml"  # 自定义配置文件路径

# 运行处理脚本
python3 auto_process_gitlab_issues.py
