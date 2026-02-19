#!/usr/bin/env python3
"""
GitLab AI Agent MCP Server

MCP (Model Context Protocol) Server for Claude Code integration
"""

import json
import sys
import os
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.gitlab import GitLabClient
from core.state import StateManager


# MCP Server 配置
MCP_SERVER_NAME = "gitissue-ai-agent"
MCP_SERVER_VERSION = "0.1.0"


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_config():
    """加载配置"""
    import yaml
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def handle_mcp_request(method: str, params: dict) -> dict:
    """
    处理 MCP 请求

    Args:
        method: MCP 方法名
        params: 参数

    Returns:
        响应数据
    """
    logger = logging.getLogger(__name__)

    if method == "tools/list":
        # 列出可用工具
        return {
            "tools": [
                {
                    "name": "gitlab_fetch_issues",
                    "description": "从 GitLab 获取分配给用户的 issues",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "GitLab 用户名"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "过滤标签"
                            }
                        },
                        "required": ["username"]
                    }
                },
                {
                    "name": "gitlab_analyze_issue",
                    "description": "分析单个 GitLab issue 并决定如何处理",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue 完整引用 (如 'group/project#123')"
                            }
                        },
                        "required": ["issue_id"]
                    }
                },
                {
                    "name": "gitlab_fix_issue",
                    "description": "自动修复 GitLab issue（克隆代码、修改、测试、创建 MR）",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue 完整引用"
                            },
                            "plan": {
                                "type": "string",
                                "description": "修复计划"
                            }
                        },
                        "required": ["issue_id", "plan"]
                    }
                },
                {
                    "name": "gitlab_comment",
                    "description": "在 GitLab issue 上添加评论",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue 完整引用"
                            },
                            "comment": {
                                "type": "string",
                                "description": "评论内容"
                            }
                        },
                        "required": ["issue_id", "comment"]
                    }
                }
            ]
        }

    elif method == "tools/call":
        # 执行工具
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        config = get_config()
        gitlab = GitLabClient(
            url=config['gitlab']['url'],
            token=config['gitlab']['access_token']
        )

        if tool_name == "gitlab_fetch_issues":
            username = arguments.get("username")
            labels = arguments.get("labels")
            issues = gitlab.get_assigned_issues(username, labels)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "count": len(issues),
                            "issues": [
                                {
                                    "id": issue['references']['full'],
                                    "title": issue['title'],
                                    "author": issue['author']['username'],
                                    "labels": issue.get('labels', []),
                                    "url": issue['web_url']
                                }
                                for issue in issues
                            ]
                        }, indent=2, ensure_ascii=False)
                    }
                ]
            }

        elif tool_name == "gitlab_analyze_issue":
            issue_id = arguments.get("issue_id")
            # 解析 issue_id (format: "group/project#123")
            parts = issue_id.split('#')
            project_path = parts[0]
            issue_iid = int(parts[1])

            # 获取项目信息
            project_info = gitlab.get_project_info(project_path)

            # 获取 issue 详情
            issue = gitlab.get_issue_by_id(str(project_info['id']), issue_iid)

            # 返回详细信息供 Claude 分析
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "issue": {
                                "id": issue['iid'],
                                "title": issue['title'],
                                "description": issue.get('description', ''),
                                "author": issue['author']['username'],
                                "labels": issue.get('labels', []),
                                "url": issue['web_url']
                            },
                            "project": {
                                "name": project_info['name'],
                                "path": project_info['path_with_namespace'],
                                "url": project_info['http_url_to_repo'],
                                "default_branch": project_info.get('default_branch', 'main')
                            },
                            "message": "请分析此 issue 并决定如何处理"
                        }, indent=2, ensure_ascii=False)
                    }
                ]
            }

        elif tool_name == "gitlab_comment":
            issue_id = arguments.get("issue_id")
            comment = arguments.get("comment")

            parts = issue_id.split('#')
            project_path = parts[0]
            issue_iid = int(parts[1])

            project_info = gitlab.get_project_info(project_path)
            result = gitlab.add_comment(str(project_info['id']), issue_iid, comment)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ 评论已发送到 {issue_id}"
                    }
                ]
            }

        elif tool_name == "gitlab_fix_issue":
            issue_id = arguments.get("issue_id")
            plan = arguments.get("plan")

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""🔧 准备修复 {issue_id}

修复计划：
{plan}

接下来我将：
1. 克隆代码仓库
2. 创建修复分支
3. 实施代码修改
4. 运行测试
5. 提交并推送
6. 创建 Merge Request
7. 在 issue 中评论

开始执行...
"""
                    }
                ]
            }

    else:
        return {"error": f"Unknown method: {method}"}


def main():
    """MCP Server 主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting {MCP_SERVER_NAME} MCP Server v{MCP_SERVER_VERSION}")

    # MCP 使用 stdio 通信
    # 读取 JSON-RPC 请求，返回 JSON-RPC 响应

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            logger.info(f"Received request: {method}")

            result = handle_mcp_request(method, params)

            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

            print(json.dumps(response))
            sys.stdout.flush()

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
