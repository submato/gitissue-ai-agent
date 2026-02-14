#!/usr/bin/env python3
"""
示例：手动处理特定 issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import argparse
from core.gitlab import GitLabClient
from core.state import StateManager
from core.agent import IssueAgent
from providers.claude import ClaudeProvider


def main():
    parser = argparse.ArgumentParser(description='手动处理特定 GitLab issue')
    parser.add_argument('issue_id', help='Issue ID (格式: project/path#123)')
    parser.add_argument('--force', action='store_true', help='强制重新处理已处理的 issue')
    args = parser.parse_args()

    # 解析 issue ID
    if '#' not in args.issue_id:
        print("❌ Issue ID 格式错误，应为: project/path#123")
        return 1

    project_path, issue_iid = args.issue_id.split('#')
    issue_iid = int(issue_iid)

    print(f"🔍 处理 Issue: {args.issue_id}")
    print()

    # 加载配置
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # 初始化组件
    gitlab = GitLabClient(
        url=config['gitlab']['url'],
        token=config['gitlab']['access_token']
    )

    state = StateManager(config.get('state_file', 'state.json'))

    ai_provider = ClaudeProvider(
        api_key=config['ai_provider']['claude']['api_key'],
        api_base=config['ai_provider']['claude'].get('api_base'),
        model=config['ai_provider']['claude']['model']
    )

    agent = IssueAgent(gitlab, ai_provider, state)

    # 检查是否已处理
    if state.is_processed(project_path, issue_iid) and not args.force:
        status = state.get_issue_status(project_path, issue_iid)
        print(f"⚠️  此 issue 已处理过，状态: {status}")
        print("💡 使用 --force 强制重新处理")
        return 0

    # 获取项目信息
    try:
        project_info = gitlab.get_project_info(project_path)
        print(f"📦 项目: {project_info['name']}")
    except Exception as e:
        print(f"❌ 获取项目信息失败: {e}")
        return 1

    # 获取 issue 详情
    try:
        issue = gitlab.get_issue_by_id(str(project_info['id']), issue_iid)
        print(f"📝 标题: {issue['title']}")
        print(f"👤 作者: @{issue['author']['username']}")
        print(f"🏷️  标签: {', '.join(issue.get('labels', []))}")
        print()
    except Exception as e:
        print(f"❌ 获取 issue 失败: {e}")
        return 1

    # 处理 issue
    try:
        result = agent.process_single_issue(issue)
        print()
        print(f"✅ 处理完成，状态: {result}")
        return 0
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
