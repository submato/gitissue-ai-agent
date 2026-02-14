#!/usr/bin/env python3
"""
GitLab AI Agent 测试脚本
用于验证各个组件的功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
from core.gitlab import GitLabClient
from core.state import StateManager
from core.agent import IssueAgent
from providers.claude import ClaudeProvider


def test_gitlab_connection():
    """测试 GitLab 连接"""
    print("🔍 测试 GitLab 连接...")

    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    gitlab = GitLabClient(
        url=config['gitlab']['url'],
        token=config['gitlab']['access_token']
    )

    try:
        issues = gitlab.get_assigned_issues(
            username=config['gitlab']['assignee_username']
        )
        print(f"✅ 成功！找到 {len(issues)} 个 issues")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_state_manager():
    """测试状态管理"""
    print("\n🔍 测试状态管理...")

    state = StateManager("test_state.json")

    # 测试标记
    state.mark_processed("test/project", 123, "completed", mr_url="https://test.com/mr/1")

    # 测试检查
    is_processed = state.is_processed("test/project", 123)

    if is_processed:
        print("✅ 状态管理正常")
        # 清理测试文件
        import os
        os.remove("test_state.json")
        return True
    else:
        print("❌ 状态管理失败")
        return False


def test_ai_provider():
    """测试 AI Provider"""
    print("\n🔍 测试 AI Provider...")

    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    try:
        provider = ClaudeProvider(
            api_key=config['ai_provider']['claude']['api_key'],
            api_base=config['ai_provider']['claude'].get('api_base'),
            model=config['ai_provider']['claude']['model']
        )
        print("✅ AI Provider 初始化成功")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_mcp_server():
    """测试 MCP Server"""
    print("\n🔍 测试 MCP Server...")

    import subprocess
    import json

    # 测试 MCP tools list
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    try:
        proc = subprocess.Popen(
            ["python3", "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = proc.communicate(input=json.dumps(request) + "\n", timeout=5)

        if "gitlab_fetch_issues" in stdout:
            print("✅ MCP Server 工作正常")
            return True
        else:
            print("❌ MCP Server 响应异常")
            return False

    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("="*60)
    print("GitLab AI Agent - 组件测试")
    print("="*60)

    results = {
        "GitLab 连接": test_gitlab_connection(),
        "状态管理": test_state_manager(),
        "AI Provider": test_ai_provider(),
        "MCP Server": test_mcp_server()
    }

    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)

    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！Agent 已准备就绪。")
    else:
        print("⚠️  部分测试失败，请检查配置。")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
