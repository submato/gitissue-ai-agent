#!/usr/bin/env python3
"""
简单的轮询脚本 - 定期检查并处理带 'bot' 标签的 issues
无需 Flask，无需 Webhook，只需定时运行即可
"""

import os
import sys
import json
import time
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
        logging.FileHandler('logs/auto_process.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 状态文件，记录已处理的 issues
STATE_FILE = 'logs/processed_issues.json'


def load_processed_issues():
    """加载已处理的 issues 列表"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_processed_issues(processed):
    """保存已处理的 issues 列表"""
    os.makedirs('logs', exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(processed, f, indent=2)


def process_issues():
    """检查并处理带 bot 标签的 issues"""

    # 从环境变量获取配置
    github_token = os.getenv('GITHUB_TOKEN')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', 'any_value')
    repo_owner = os.getenv('REPO_OWNER', 'submato')
    repo_name = os.getenv('REPO_NAME', 'gitissue-ai-agent')
    use_local_proxy = os.getenv('USE_LOCAL_PROXY', '1')

    if not github_token:
        logger.error("GITHUB_TOKEN environment variable not set")
        return

    logger.info(f"Checking issues in {repo_owner}/{repo_name}")

    # 初始化客户端
    github_client = GitHubClient(
        token=github_token,
        repo_owner=repo_owner,
        repo_name=repo_name
    )

    # 初始化 AI Provider
    api_base = "http://localhost:8082" if use_local_proxy == '1' else None
    ai_provider = ClaudeProvider(
        api_key=anthropic_api_key,
        model="claude-sonnet-4-5-20250929",
        api_base=api_base
    )

    # 加载已处理的 issues
    processed = load_processed_issues()

    try:
        # 获取所有带 'bot' 标签且 open 状态的 issues
        issues = github_client.get_repository_issues(
            labels=['bot'],
            state='open'
        )

        logger.info(f"Found {len(issues)} open issues with 'bot' label")

        for issue in issues:
            issue_number = issue['number']
            issue_key = f"{repo_owner}/{repo_name}#{issue_number}"

            # 获取评论历史
            comments = github_client.get_comments(issue_number)

            # 生成此 issue 的"状态指纹"（用于判断是否有新变化）
            # 包含：issue 标题、描述、评论数
            fingerprint = f"{issue['title']}_{issue['body']}_{len(comments)}"

            # 检查是否已处理过且没有新变化
            if issue_key in processed and processed[issue_key] == fingerprint:
                logger.debug(f"Issue #{issue_number} already processed, skipping")
                continue

            logger.info(f"Processing issue #{issue_number}: {issue['title']}")

            # 发布开始处理的评论
            try:
                start_comment = f"""🤖 **AI Agent 已开始处理此 issue，请稍等...**

正在分析 issue 内容，很快会给出反馈。

⏳ *Processing...*
"""
                github_client.add_comment(issue_number, start_comment)
                logger.info(f"Posted 'start processing' comment on issue #{issue_number}")
            except Exception as e:
                logger.error(f"Failed to post start comment: {e}")

            # 添加 analyzing 标签
            try:
                current_labels = [label['name'] for label in issue.get('labels', [])]
                if 'analyzing' not in current_labels:
                    github_client.add_labels(issue_number, ['analyzing'])
                    logger.info(f"Added 'analyzing' label to issue #{issue_number}")
            except Exception as e:
                logger.error(f"Failed to add label: {e}")

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
                if '🤖' not in body and 'AI Agent' not in body and 'Powered by' not in body:
                    user_comments.append({
                        'author': author,
                        'body': body,
                        'created_at': comment['created_at']
                    })

            # AI 分析
            try:
                analysis_result = ai_provider.analyze_issue(unified_issue, repo_info, user_comments)
                logger.info(f"AI Analysis for #{issue_number}: {analysis_result.get('action')}")

                # 根据分析结果采取行动
                action = analysis_result.get('action', 'skip')

                if action == "need_info":
                    questions = analysis_result.get('questions', [])
                    questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

                    comment_body = f"""👋 Hi @{issue['user']['login']}!

I've analyzed your issue and need some more information to proceed:

{questions_text}

**Reason:** {analysis_result.get('reason', 'Need clarification')}

Once you provide these details, I'll be able to help with this issue automatically.

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body)

                    # 更新标签
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('needs-info')
                    github_client.update_issue_labels(issue_number, new_labels)

                elif action == "can_handle":
                    plan = analysis_result.get('plan', 'Will work on this issue')

                    comment_body = f"""✅ Great! I can help with this issue.

**Analysis:**
{analysis_result.get('reason', 'This issue can be automated')}

**Plan:**
{plan}

I'll start working on this shortly. Stay tuned for updates!

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body)

                    # 更新标签
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('in-progress')
                    github_client.update_issue_labels(issue_number, new_labels)

                else:  # skip
                    comment_body = f"""ℹ️ I've analyzed this issue, but it appears to be too complex for automatic handling.

**Reason:**
{analysis_result.get('reason', 'This task requires human expertise')}

This issue would benefit from human review and implementation. I'll label it appropriately for the team to review.

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, comment_body)

                    # 更新标签
                    new_labels = [l for l in current_labels if l != 'analyzing']
                    new_labels.append('cannot-fix')
                    github_client.update_issue_labels(issue_number, new_labels)

                # 记录已处理
                processed[issue_key] = fingerprint
                save_processed_issues(processed)

                logger.info(f"✅ Successfully processed issue #{issue_number}")

            except Exception as e:
                logger.error(f"Error analyzing issue #{issue_number}: {e}")

                # 发布错误评论
                try:
                    error_comment = f"""❌ Oops! I encountered an error while processing this issue:

```
{str(e)}
```

The team has been notified and will look into this.

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
                    github_client.add_comment(issue_number, error_comment)
                except:
                    pass

    except Exception as e:
        logger.error(f"Error fetching issues: {e}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting automatic issue processing")
    logger.info("=" * 60)

    process_issues()

    logger.info("=" * 60)
    logger.info("Finished processing")
    logger.info("=" * 60)
