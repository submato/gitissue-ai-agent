#!/usr/bin/env python3
"""
GitLab AI Agent 主程序
"""

import sys
import argparse
import logging
import yaml
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.gitlab import GitLabClient
from core.agent import IssueAgent
from core.state import StateManager
from providers.claude import ClaudeProvider


def load_config(config_file: str = "config/config.yaml") -> dict:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logging(config: dict):
    """配置日志"""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    format_str = log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')

    handlers = [logging.StreamHandler()]

    # 如果配置了日志文件
    log_file = log_config.get('file')
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )


def create_ai_provider(config: dict):
    """根据配置创建 AI Provider"""
    provider_config = config['ai_provider']
    provider_type = provider_config['type']

    if provider_type == 'claude':
        claude_config = provider_config['claude']
        return ClaudeProvider(
            api_key=claude_config['api_key'],
            model=claude_config.get('model', 'claude-sonnet-4-5-20250929'),
            api_base=claude_config.get('api_base')
        )
    else:
        raise ValueError(f"不支持的 AI provider 类型: {provider_type}")


def print_banner():
    """打印欢迎信息"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║            GitLab AI Agent 🤖                              ║
║                                                            ║
║     Automatically solve GitLab issues with AI              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")


def print_statistics(stats: dict):
    """打印统计信息"""
    print("\n" + "="*60)
    print("📊 处理统计")
    print("="*60)
    print(f"  总计: {stats['total']}")
    print(f"  ✅ 完成: {stats.get('completed', 0)}")
    print(f"  🔄 进行中: {stats.get('in_progress', 0)}")
    print(f"  ❓ 等待信息: {stats.get('waiting_for_info', 0)}")
    print(f"  ⏭️  跳过: {stats.get('skipped', 0)}")
    print(f"  ❌ 失败: {stats.get('failed', 0)}")

    if stats['total'] > 0:
        success_rate = (stats.get('completed', 0) / stats['total']) * 100
        print(f"\n  📈 成功率: {success_rate:.1f}%")

    print("="*60 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GitLab AI Agent')
    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='配置文件路径 (默认: config/config.yaml)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='只显示统计信息'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式（不实际执行）'
    )

    args = parser.parse_args()

    # 打印欢迎信息
    print_banner()

    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {args.config}")
        print(f"💡 请复制 config/config.example.yaml 到 {args.config} 并编辑")
        sys.exit(1)

    # 配置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # 创建状态管理器
    state_manager = StateManager(config.get('state_file', 'state.json'))

    # 如果只是查看统计
    if args.stats:
        stats = state_manager.get_statistics()
        print_statistics(stats)
        return

    # 创建 GitLab 客户端
    gitlab_config = config['gitlab']
    gitlab_client = GitLabClient(
        url=gitlab_config['url'],
        token=gitlab_config['access_token']
    )

    # 创建 AI Provider
    try:
        ai_provider = create_ai_provider(config)
    except Exception as e:
        logger.error(f"❌ 创建 AI Provider 失败: {e}")
        sys.exit(1)

    # 创建 Agent
    agent = IssueAgent(gitlab_client, ai_provider, state_manager)

    # 开始处理
    logger.info("🚀 开始处理 issues...\n")

    try:
        results = agent.process_all_issues(
            username=gitlab_config['assignee_username'],
            labels=gitlab_config.get('auto_process_labels')
        )

        # 打印结果
        print_statistics(results)
        logger.info("✅ 处理完成！")

    except KeyboardInterrupt:
        logger.info("\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 处理失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
