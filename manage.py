#!/usr/bin/env python3
"""
GitLab AI Agent 管理工具
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import argparse
import json
from datetime import datetime
from core.state import StateManager
from core.gitlab import GitLabClient


def cmd_stats(args):
    """显示统计信息"""
    state = StateManager(args.state_file)
    stats = state.get_statistics()

    print("="*60)
    print("📊 GitLab AI Agent 统计")
    print("="*60)
    print(f"总处理数: {stats['total']}")
    print(f"  ✅ 完成: {stats.get('completed', 0)}")
    print(f"  🔄 进行中: {stats.get('in_progress', 0)}")
    print(f"  ❓ 等待信息: {stats.get('waiting_for_info', 0)}")
    print(f"  ⏭️  跳过: {stats.get('skipped', 0)}")
    print(f"  ❌ 失败: {stats.get('failed', 0)}")

    if stats['total'] > 0:
        success_rate = (stats.get('completed', 0) / stats['total']) * 100
        print(f"\n📈 成功率: {success_rate:.1f}%")

    # 显示最近处理的 issues
    all_issues = state.get_all_processed_issues()
    if all_issues:
        print(f"\n📋 最近处理的 issues:")
        sorted_issues = sorted(
            all_issues.items(),
            key=lambda x: x[1].get('processed_at', ''),
            reverse=True
        )
        for issue_key, data in sorted_issues[:5]:
            status = data['status']
            time = data.get('processed_at', 'N/A')[:19]  # 截取到秒
            print(f"  {issue_key} - {status} ({time})")

    print("="*60)


def cmd_list_issues(args):
    """列出 GitLab issues"""
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    gitlab = GitLabClient(
        url=config['gitlab']['url'],
        token=config['gitlab']['access_token']
    )

    print("🔍 获取 issues...")

    issues = gitlab.get_assigned_issues(
        username=config['gitlab']['assignee_username'],
        labels=args.labels.split(',') if args.labels else None
    )

    print(f"\n找到 {len(issues)} 个 issues:\n")

    for issue in issues:
        project = issue['references']['full'].split('#')[0]
        labels = ', '.join(issue.get('labels', []))
        print(f"📌 {issue['references']['full']}")
        print(f"   标题: {issue['title']}")
        print(f"   项目: {project}")
        print(f"   标签: {labels or '(无)'}")
        print(f"   URL: {issue['web_url']}")
        print()


def cmd_reset(args):
    """重置状态"""
    if not args.confirm:
        print("⚠️  此操作将清除所有处理记录！")
        response = input("确认重置？输入 'yes' 继续: ")
        if response.lower() != 'yes':
            print("已取消")
            return

    state = StateManager(args.state_file)
    state.state = {
        "processed_issues": {},
        "last_run": None,
        "statistics": {
            "total": 0,
            "completed": 0,
            "waiting_for_info": 0,
            "in_progress": 0,
            "failed": 0
        }
    }
    state._save_state()
    print("✅ 状态已重置")


def cmd_config(args):
    """显示配置信息"""
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    print("="*60)
    print("⚙️  GitLab AI Agent 配置")
    print("="*60)
    print(f"GitLab URL: {config['gitlab']['url']}")
    print(f"用户名: {config['gitlab']['assignee_username']}")
    print(f"自动处理标签: {', '.join(config['gitlab']['auto_process_labels'])}")
    print(f"AI Provider: {config['ai_provider']['type']}")
    print(f"模型: {config['ai_provider']['claude']['model']}")
    print(f"工作空间: {config['workspace']['clone_path']}")
    print(f"状态文件: {config['state_file']}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='GitLab AI Agent 管理工具'
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='配置文件路径'
    )

    parser.add_argument(
        '--state-file',
        default='state.json',
        help='状态文件路径'
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # stats 命令
    subparsers.add_parser('stats', help='显示统计信息')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出 GitLab issues')
    list_parser.add_argument('--labels', help='过滤标签 (逗号分隔)')

    # reset 命令
    reset_parser = subparsers.add_parser('reset', help='重置状态')
    reset_parser.add_argument('--confirm', action='store_true', help='跳过确认')

    # config 命令
    subparsers.add_parser('config', help='显示配置')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 执行命令
    if args.command == 'stats':
        cmd_stats(args)
    elif args.command == 'list':
        cmd_list_issues(args)
    elif args.command == 'reset':
        cmd_reset(args)
    elif args.command == 'config':
        cmd_config(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
