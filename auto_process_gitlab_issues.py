#!/usr/bin/env python3
"""
GitLab 自动处理脚本 - 定期检查并处理 GitLab issues
类似 GitHub 的 auto_process_issues.py
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.gitlab import GitLabClient
from core.agent import IssueAgent
from core.state import StateManager
from providers.claude import ClaudeProvider

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gitlab_auto_process.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    """加载配置文件"""
    config_file = os.getenv('GITLAB_CONFIG_FILE', 'config/config.yaml')

    if not os.path.exists(config_file):
        logger.error(f"配置文件不存在: {config_file}")
        logger.info("请创建配置文件或设置 GITLAB_CONFIG_FILE 环境变量")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Starting GitLab automatic issue processing")
    logger.info("=" * 60)

    # 加载配置
    config = load_config()

    # 创建 GitLab 客户端
    gitlab_config = config['gitlab']
    gitlab_client = GitLabClient(
        url=gitlab_config['url'],
        token=gitlab_config['access_token']
    )
    logger.info(f"GitLab URL: {gitlab_config['url']}")

    # 创建 AI Provider
    provider_config = config['ai_provider']
    if provider_config['type'] == 'claude':
        claude_config = provider_config['claude']

        # 支持本地代理
        use_local_proxy = os.getenv('USE_LOCAL_PROXY', '0')
        api_base = claude_config.get('api_base')
        if use_local_proxy == '1' and not api_base:
            api_base = "http://localhost:8082"

        ai_provider = ClaudeProvider(
            api_key=claude_config['api_key'],
            model=claude_config.get('model', 'claude-sonnet-4-5-20250929'),
            api_base=api_base
        )
        logger.info(f"AI Provider: Claude (api_base: {api_base or 'official'})")
    else:
        logger.error(f"不支持的 AI provider: {provider_config['type']}")
        sys.exit(1)

    # 创建状态管理器
    state_manager = StateManager(config.get('state_file', 'state.json'))

    # 创建 Agent
    agent = IssueAgent(gitlab_client, ai_provider, state_manager)

    # 处理 issues
    try:
        results = agent.process_all_issues(
            username=gitlab_config.get('assignee_username'),
            labels=gitlab_config.get('auto_process_labels', ['bot', 'auto-fix', 'ai'])
        )

        logger.info("=" * 60)
        logger.info("Processing completed")
        logger.info(f"Total: {results.get('total', 0)}")
        logger.info(f"Completed: {results.get('completed', 0)}")
        logger.info(f"In Progress: {results.get('in_progress', 0)}")
        logger.info(f"Waiting for Info: {results.get('waiting_for_info', 0)}")
        logger.info(f"Skipped: {results.get('skipped', 0)}")
        logger.info(f"Failed: {results.get('failed', 0)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error processing issues: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
