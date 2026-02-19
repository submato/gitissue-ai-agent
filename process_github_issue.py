#!/usr/bin/env python3
"""
GitHub Issue 处理脚本
用于 GitHub Actions 中自动处理 issues
"""

import os
import sys
import logging
from datetime import datetime
from core.github import GitHubClient
from providers.claude import ClaudeProvider


def setup_logging(issue_number):
    """设置日志，同时输出到控制台和文件"""
    # 创建 logs 目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件名包含 issue 号和时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"github_issue_{issue_number}_{timestamp}.log")

    # 配置日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # 创建 logger
    logger = logging.getLogger('GitHubIssueAgent')
    logger.setLevel(logging.INFO)

    # 清除已有的 handlers
    logger.handlers = []

    # 文件 handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    logger.info(f"Logging to: {log_file}")
    return logger, log_file


def main():
    # 从环境变量获取配置
    github_token = os.getenv('GITHUB_TOKEN')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')

    if not all([github_token, anthropic_api_key, issue_number, repo_owner, repo_name]):
        logger.info("Error: Missing required environment variables")
        sys.exit(1)

    # 设置日志
    logger, log_file = setup_logging(issue_number)
    logger.info(f"Processing issue #{issue_number} in {repo_owner}/{repo_name}")

    # 初始化客户端
    github_client = GitHubClient(
        token=github_token,
        repo_owner=repo_owner,
        repo_name=repo_name
    )

    # 初始化 AI Provider
    ai_provider = ClaudeProvider(
        api_key=anthropic_api_key,
        model="claude-sonnet-4-5-20250929",
        api_base="http://localhost:8082"  # 使用本地代理
    )

    try:
        # 获取 issue 详情
        issue = github_client.get_issue_by_number(issue_number)

        logger.info(f"Issue title: {issue['title']}")
        logger.info(f"Issue body: {issue['body'][:200]}...")  # 打印前200字符

        # 获取所有评论（包括用户的回复）
        comments = github_client.get_comments(issue_number)
        logger.info(f"Found {len(comments)} comments on this issue")

        # 过滤掉机器人自己的评论，只保留用户评论
        user_comments = []
        for comment in comments:
            author = comment['user']['login']
            body = comment['body']
            # 跳过 bot 自己的评论
            if '🤖' not in body and 'AI Agent' not in body and 'Powered by' not in body:
                user_comments.append({
                    'author': author,
                    'body': body,
                    'created_at': comment['created_at']
                })
                logger.info(f"User comment from @{author}: {body[:100]}...")

        # 立即发布开始处理的评论
        start_comment = f"""🤖 **AI Agent 已开始处理此 issue，请稍等...**

正在分析 issue 内容，很快会给出反馈。

⏳ *Processing...*
"""
        github_client.add_comment(issue_number, start_comment)
        logger.info("Posted 'start processing' comment")

        # 添加 analyzing 标签
        current_labels = [label['name'] for label in issue.get('labels', [])]
        if 'analyzing' not in current_labels:
            github_client.add_labels(issue_number, ['analyzing'])
            logger.info("Added 'analyzing' label")

        # 构建仓库信息（用于 AI 分析）
        repo_info = {
            'name': repo_name,
            'path_with_namespace': f"{repo_owner}/{repo_name}",
            'default_branch': 'main',
            'description': f"GitHub repository: {repo_owner}/{repo_name}"
        }

        # 转换 GitHub issue 格式为统一格式
        unified_issue = {
            'iid': issue['number'],
            'title': issue['title'],
            'description': issue['body'] or '',
            'author': {
                'username': issue['user']['login']
            },
            'labels': [label['name'] for label in issue.get('labels', [])]
        }

        logger.info("\nAnalyzing issue with AI...")
        analysis_result = ai_provider.analyze_issue(unified_issue, repo_info, user_comments)
        logger.info(f"AI Analysis: {analysis_result}")

        # 根据分析结果采取行动
        action = analysis_result.get('action', 'skip')

        if action == "need_info":
            # 需要更多信息
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

            logger.info("Posted comment asking for more info")

        elif action == "can_handle":
            # 可以处理
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

            logger.info("Posted comment confirming can handle")
            logger.info("Note: Actual implementation would be done here")

        else:  # skip or other
            # 无法自动处理
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

            logger.info("Posted comment explaining cannot handle")

        logger.info(f"\n✅ Successfully processed issue #{issue_number}")
        logger.info(f"📁 Log saved to: {log_file}")

    except Exception as e:
        logger.error(f"Error processing issue: {e}")

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

        sys.exit(1)


if __name__ == "__main__":
    main()
