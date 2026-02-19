#!/usr/bin/env python3
"""
GitHub 多仓库自动处理脚本
支持在一次运行中处理多个 GitHub 仓库的 issues
"""

import os
import sys
import json
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.github import GitHubClient
from providers.claude import ClaudeProvider

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/github_multi_repo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 状态文件
STATE_FILE = 'logs/github_multi_repo_state.json'


def load_processed_issues():
    """加载已处理的 issues"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_processed_issues(processed):
    """保存已处理的 issues"""
    os.makedirs('logs', exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(processed, f, indent=2)


def process_repository(github_client, ai_provider, repo_owner, repo_name, processed):
    """处理单个仓库的 issues"""

    logger.info(f"\n{'='*60}")
    logger.info(f"Processing repository: {repo_owner}/{repo_name}")
    logger.info(f"{'='*60}")

    try:
        # 获取带 'bot' 标签的 open issues
        issues = github_client.get_repository_issues(
            owner=repo_owner,
            repo=repo_name,
            labels=['bot'],
            state='open'
        )

        logger.info(f"Found {len(issues)} open issues with 'bot' label")

        processed_count = 0
        for issue in issues:
            issue_number = issue['number']
            issue_key = f"{repo_owner}/{repo_name}#{issue_number}"

            # 获取评论
            comments = github_client.get_comments(issue_number, repo_owner, repo_name)

            # 生成指纹
            fingerprint = f"{issue['title']}_{issue['body']}_{len(comments)}"

            # 检查是否已处理
            if issue_key in processed and processed[issue_key] == fingerprint:
                logger.debug(f"Issue #{issue_number} already processed, skipping")
                continue

            logger.info(f"Processing issue #{issue_number}: {issue['title']}")

            try:
                # 发布开始处理评论
                start_comment = """🤖 **AI Agent 已开始处理此 issue，请稍等...**

正在分析 issue 内容，很快会给出反馈。

⏳ *Processing...*
"""
                github_client.add_comment(issue_number, start_comment, repo_owner, repo_name)

                # 添加 analyzing 标签
                current_labels = [label['name'] for label in issue.get('labels', [])]
                if 'analyzing' not in current_labels:
                    github_client.add_labels(issue_number, ['analyzing'], repo_owner, repo_name)

                # 构建仓库信息
                repo_info = {
                    'name': repo_name,
                    'path_with_namespace': f"{repo_owner}/{repo_name}",
                    'default_branch': 'main',
                    'description': f"GitHub repository: {repo_owner}/{repo_name}"
                }

                # 转换为统一格式
                unified_issue = {
                    'iid': issue['number'],
                    'title': issue['title'],
                    'description': issue['body'] or '',
                    'author': {
                        'username': issue['user']['login']
                    },
                    'labels': [label['name'] for label in issue.get('labels', [])]
                }

                # 过滤用户评论
                user_comments = []
                for comment in comments:
                    author = comment['user']['login']
                    body = comment['body']
                    if '🤖' not in body and 'AI Agent' not in body:
                        user_comments.append({
                            'author': author,
                            'body': body,
                            'created_at': comment['created_at']
                        })

                # AI 分析
                analysis_result = ai_provider.analyze_issue(unified_issue, repo_info, user_comments)
                action = analysis_result.get('action', 'skip')

                logger.info(f"AI Analysis: {action}")

                # 根据结果采取行动
                if action == "need_info":
                    questions = analysis_result.get('questions', [])
                    questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

                    comment_body = f"""👋 Hi @{issue['user']['login']}!

I've analyzed your issue and need some more information:

{questions_text}

**Reason:** {analysis_result.get('reason', 'Need clarification')}

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body, repo_owner, repo_name)
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('needs-info')
                    github_client.update_issue_labels(issue_number, new_labels, repo_owner, repo_name)

                elif action == "can_handle":
                    plan = analysis_result.get('plan', 'Will work on this issue')

                    comment_body = f"""✅ Great! I can help with this issue.

**Analysis:**
{analysis_result.get('reason', 'This issue can be automated')}

**Plan:**
{plan}

I'll start working on this shortly!

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body, repo_owner, repo_name)
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('in-progress')
                    github_client.update_issue_labels(issue_number, new_labels, repo_owner, repo_name)

                else:  # skip
                    comment_body = f"""ℹ️ I've analyzed this issue, but it requires human expertise.

**Reason:**
{analysis_result.get('reason', 'This task requires human review')}

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body, repo_owner, repo_name)
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('cannot-fix')
                    github_client.update_issue_labels(issue_number, new_labels, repo_owner, repo_name)

                # 记录已处理
                processed[issue_key] = fingerprint
                processed_count += 1
                logger.info(f"✅ Successfully processed issue #{issue_number}")

            except Exception as e:
                logger.error(f"Error processing issue #{issue_number}: {e}")

        return processed_count

    except Exception as e:
        logger.error(f"Error fetching issues from {repo_owner}/{repo_name}: {e}")
        return 0


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Starting GitHub multi-repository processing")
    logger.info("=" * 60)

    # 从环境变量获取配置
    github_token = os.getenv('GITHUB_TOKEN')
    repositories_str = os.getenv('GITHUB_REPOS', '')  # 格式: owner1/repo1,owner2/repo2
    use_local_proxy = os.getenv('USE_LOCAL_PROXY', '1')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', 'any_value')

    if not github_token:
        logger.error("GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    if not repositories_str:
        logger.error("GITHUB_REPOS environment variable not set")
        logger.info("Format: GITHUB_REPOS='owner1/repo1,owner2/repo2'")
        sys.exit(1)

    # 解析仓库列表
    repositories = []
    for repo_str in repositories_str.split(','):
        repo_str = repo_str.strip()
        if '/' not in repo_str:
            logger.warning(f"Invalid repository format: {repo_str} (expected: owner/repo)")
            continue
        owner, repo = repo_str.split('/', 1)
        repositories.append((owner, repo))

    if not repositories:
        logger.error("No valid repositories found")
        sys.exit(1)

    logger.info(f"Will process {len(repositories)} repositories:")
    for owner, repo in repositories:
        logger.info(f"  - {owner}/{repo}")

    # 初始化客户端
    github_client = GitHubClient(token=github_token)

    # 初始化 AI Provider
    api_base = "http://localhost:8082" if use_local_proxy == '1' else None
    ai_provider = ClaudeProvider(
        api_key=anthropic_api_key,
        model="claude-sonnet-4-5-20250929",
        api_base=api_base
    )

    # 加载已处理记录
    processed = load_processed_issues()

    # 处理每个仓库
    total_processed = 0
    for repo_owner, repo_name in repositories:
        count = process_repository(github_client, ai_provider, repo_owner, repo_name, processed)
        total_processed += count

    # 保存状态
    save_processed_issues(processed)

    logger.info("\n" + "=" * 60)
    logger.info(f"Finished processing {len(repositories)} repositories")
    logger.info(f"Total issues processed: {total_processed}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
