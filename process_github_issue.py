#!/usr/bin/env python3
"""
GitHub Issue 处理脚本
用于 GitHub Actions 中自动处理 issues
"""

import os
import sys
from core.github import GitHubClient
from providers.claude import ClaudeProvider


def main():
    # 从环境变量获取配置
    github_token = os.getenv('GITHUB_TOKEN')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')

    if not all([github_token, anthropic_api_key, issue_number, repo_owner, repo_name]):
        print("Error: Missing required environment variables")
        sys.exit(1)

    print(f"Processing issue #{issue_number} in {repo_owner}/{repo_name}")

    # 初始化客户端
    github_client = GitHubClient(
        token=github_token,
        repo_owner=repo_owner,
        repo_name=repo_name
    )

    # 初始化 AI Provider
    ai_provider = ClaudeProvider(
        api_key=anthropic_api_key,
        model="claude-sonnet-4-5-20250929"
    )

    try:
        # 获取 issue 详情
        issue = github_client.get_issue_by_number(issue_number)

        print(f"Issue title: {issue['title']}")
        print(f"Issue body: {issue['body'][:200]}...")  # 打印前200字符

        # 添加 analyzing 标签
        current_labels = [label['name'] for label in issue.get('labels', [])]
        if 'analyzing' not in current_labels:
            github_client.add_labels(issue_number, ['analyzing'])
            print("Added 'analyzing' label")

        # 构建分析提示
        analysis_prompt = f"""
Analyze this GitHub issue and determine if it can be handled automatically:

**Issue Title:** {issue['title']}

**Issue Description:**
{issue['body']}

**Repository:** {repo_owner}/{repo_name}

Determine:
1. Can this issue be handled automatically? (yes/no)
2. What needs to be done?
3. If you need more information, what questions should be asked?

Respond in JSON format:
{{
  "can_handle": true/false,
  "decision": "can_handle" or "need_info" or "cannot_fix",
  "reason": "explanation",
  "questions": ["question1", "question2"] (if need_info),
  "plan": ["step1", "step2"] (if can_handle)
}}
"""

        print("\nAnalyzing issue with AI...")
        analysis_result = ai_provider.analyze(analysis_prompt)
        print(f"AI Analysis: {analysis_result}")

        # 根据分析结果采取行动
        if "need_info" in analysis_result.lower() or "need more" in analysis_result.lower():
            # 需要更多信息
            comment_body = f"""👋 Hi @{issue['user']['login']}!

I've analyzed your issue and need some more information to proceed:

{analysis_result}

Once you provide these details, I'll be able to help with this issue automatically.

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
            github_client.add_comment(issue_number, comment_body)

            # 更新标签
            new_labels = [l for l in current_labels if l != 'analyzing']
            new_labels.append('needs-info')
            github_client.update_issue_labels(issue_number, new_labels)

            print("Posted comment asking for more info")

        elif "can_handle" in analysis_result.lower() or "can handle" in analysis_result.lower():
            # 可以处理
            comment_body = f"""✅ Great! I can help with this issue.

**Analysis:**
{analysis_result}

I'll start working on this shortly. Stay tuned for updates!

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
            github_client.add_comment(issue_number, comment_body)

            # 更新标签
            new_labels = [l for l in current_labels if l != 'analyzing']
            new_labels.append('in-progress')
            github_client.update_issue_labels(issue_number, new_labels)

            print("Posted comment confirming can handle")
            print("Note: Actual implementation would be done here")

        else:
            # 无法自动处理
            comment_body = f"""ℹ️ I've analyzed this issue, but it appears to be too complex for automatic handling.

**Reason:**
{analysis_result}

This issue would benefit from human review and implementation. I'll label it appropriately for the team to review.

🤖 *Powered by [GitIssue AI Agent](https://github.com/{repo_owner}/{repo_name})*
"""
            github_client.add_comment(issue_number, comment_body)

            # 更新标签
            new_labels = [l for l in current_labels if l != 'analyzing']
            new_labels.append('cannot-fix')
            github_client.update_issue_labels(issue_number, new_labels)

            print("Posted comment explaining cannot handle")

        print(f"\n✅ Successfully processed issue #{issue_number}")

    except Exception as e:
        print(f"Error processing issue: {e}")

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
