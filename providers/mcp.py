"""
MCP Provider
直接在 Claude Code 环境中执行，无需 API 调用
"""

import json
import subprocess
from typing import Dict
from .base import AIProvider


class MCPProvider(AIProvider):
    """
    MCP (Model Context Protocol) Provider

    在 Claude Code 环境中直接执行任务
    不需要外部 API 调用
    """

    def __init__(self, **kwargs):
        """
        初始化 MCP Provider

        在 MCP 模式下，这个 provider 实际上是被 Claude Code 内部调用
        所以不需要 API key 或其他配置
        """
        self.mode = "mcp"

    def analyze_issue(self, issue: Dict, project_info: Dict) -> Dict:
        """
        分析 issue

        在 MCP 模式下，这个方法实际上由 Claude Code 直接执行
        我们返回一个特殊的标记，让 Claude 直接分析
        """
        # 返回特殊标记，让外部知道这需要 Claude 实时分析
        return {
            "action": "mcp_analyze",
            "issue": issue,
            "project_info": project_info,
            "message": "MCP 模式：需要 Claude 实时分析此 issue"
        }

    def generate_fix_instructions(
        self,
        issue: Dict,
        project_info: Dict,
        plan: str
    ) -> str:
        """
        在 MCP 模式下，不需要生成指令
        Claude 会直接执行操作
        """
        return f"""# MCP 模式 - 直接执行

Issue: #{issue['iid']} - {issue['title']}
Project: {project_info.get('path_with_namespace')}

处理计划：
{plan}

在 MCP 模式下，Claude 将直接执行以下操作：
1. 克隆/更新代码仓库
2. 创建修复分支
3. 实施代码修改
4. 运行测试
5. 提交并推送
6. 创建 Merge Request
7. 在 issue 中评论

无需人工干预！
"""


class MCPExecutor:
    """
    MCP 执行器

    在 Claude Code 环境中直接执行 issue 修复
    """

    def __init__(self, gitlab_client, workspace_path: str = "/tmp/gitissue-ai-agent-workspace"):
        """
        初始化执行器

        Args:
            gitlab_client: GitLab 客户端
            workspace_path: 工作空间路径
        """
        self.gitlab = gitlab_client
        self.workspace = workspace_path

    def execute_fix(self, issue: Dict, project_info: Dict, plan: str) -> Dict:
        """
        直接执行 issue 修复

        这个方法会被 Claude Code 调用，实际操作由 Claude 执行

        Args:
            issue: Issue 信息
            project_info: 项目信息
            plan: 修复计划

        Returns:
            执行结果
        """
        project_path = project_info.get('path_with_namespace')
        issue_iid = issue['iid']

        # 返回需要执行的任务描述
        # 在实际运行时，Claude Code 会看到这个并执行
        return {
            "status": "ready_to_execute",
            "task": {
                "type": "fix_gitlab_issue",
                "issue_id": issue_iid,
                "issue_title": issue['title'],
                "project": project_path,
                "project_url": project_info.get('http_url_to_repo'),
                "default_branch": project_info.get('default_branch', 'main'),
                "plan": plan,
                "steps": [
                    "clone_or_update_repo",
                    "create_branch",
                    "implement_fix",
                    "run_tests",
                    "commit_changes",
                    "push_branch",
                    "create_merge_request",
                    "comment_on_issue"
                ]
            }
        }
