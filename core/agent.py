"""
Issue Agent 核心逻辑
协调 GitLab 客户端、AI Provider 和状态管理
"""

import logging
from typing import Dict, List
from .gitlab import GitLabClient
from .state import StateManager
from providers.base import AIProvider


logger = logging.getLogger(__name__)


class IssueAgent:
    """Issue 处理 Agent"""

    def __init__(
        self,
        gitlab_client: GitLabClient,
        ai_provider: AIProvider,
        state_manager: StateManager
    ):
        """
        初始化 Agent

        Args:
            gitlab_client: GitLab 客户端
            ai_provider: AI Provider
            state_manager: 状态管理器
        """
        self.gitlab = gitlab_client
        self.ai = ai_provider
        self.state = state_manager

    def process_all_issues(
        self,
        username: str,
        labels: List[str] = None
    ) -> Dict:
        """
        处理所有分配给用户的 issues

        Args:
            username: GitLab 用户名
            labels: 过滤标签

        Returns:
            处理结果统计
        """
        logger.info(f"🔍 获取分配给 @{username} 的 issues...")

        # 获取所有 issues
        issues = self.gitlab.get_assigned_issues(username, labels)
        logger.info(f"📋 找到 {len(issues)} 个 issues")

        # 过滤未处理的 issues
        new_issues = []
        for issue in issues:
            project_path = issue['references']['full'].split('#')[0]
            if not self.state.is_processed(project_path, issue['iid']):
                new_issues.append(issue)

        logger.info(f"🆕 其中 {len(new_issues)} 个是新 issues\n")

        # 处理结果统计
        results = {
            "total": len(new_issues),
            "completed": 0,
            "waiting_for_info": 0,
            "in_progress": 0,
            "skipped": 0,
            "failed": 0
        }

        # 处理每个 issue
        for issue in new_issues:
            try:
                result = self.process_single_issue(issue)
                if result:
                    results[result] += 1
            except Exception as e:
                logger.error(f"❌ 处理 issue 失败: {e}")
                results["failed"] += 1

        return results

    def process_single_issue(self, issue: Dict) -> str:
        """
        处理单个 issue

        Args:
            issue: Issue 信息

        Returns:
            处理结果状态
        """
        # 提取项目路径
        project_path = issue['references']['full'].split('#')[0]
        issue_iid = issue['iid']

        logger.info(f"\n{'='*60}")
        logger.info(f"📌 处理 Issue: {issue['references']['full']}")
        logger.info(f"📝 标题: {issue['title']}")
        logger.info(f"👤 作者: @{issue['author']['username']}")
        logger.info(f"{'='*60}\n")

        # 获取项目信息
        try:
            project_info = self.gitlab.get_project_info(issue['project_id'])
        except Exception as e:
            logger.error(f"❌ 获取项目信息失败: {e}")
            self.state.mark_processed(
                project_path, issue_iid,
                status="failed",
                error=str(e)
            )
            return "failed"

        # AI 分析 issue
        logger.info("🤔 AI 正在分析...")
        decision = self.ai.analyze_issue(issue, project_info)

        action = decision.get("action", "skip")
        reason = decision.get("reason", "未知原因")

        logger.info(f"💡 决策: {action}")
        logger.info(f"📝 原因: {reason}\n")

        # 根据决策执行操作
        if action == "need_info":
            return self._handle_need_info(issue, project_path, project_info, decision)

        elif action == "can_handle":
            return self._handle_can_handle(issue, project_path, project_info, decision)

        elif action == "skip":
            return self._handle_skip(issue, project_path, decision)

        else:
            logger.warning(f"⚠️  未知的 action: {action}")
            return "skipped"

    def _handle_need_info(
        self,
        issue: Dict,
        project_path: str,
        project_info: Dict,
        decision: Dict
    ) -> str:
        """处理需要更多信息的情况"""
        questions = decision.get('questions', [])
        comment = decision.get('comment', '')

        # 如果没有提供评论，自动生成
        if not comment:
            comment = f"@{issue['author']['username']} 你好！我需要更多信息来处理这个 issue：\n\n"
            for i, q in enumerate(questions, 1):
                comment += f"{i}. {q}\n"
            comment += f"\n请提供这些信息，我将继续处理。谢谢！\n\n🤖 由 GitLab AI Agent 自动发送"

        logger.info(f"💬 发送评论询问信息...")

        try:
            self.gitlab.add_comment(str(issue['project_id']), issue['iid'], comment)
            logger.info("✅ 评论已发送\n")

            self.state.mark_processed(
                project_path, issue['iid'],
                status="waiting_for_info",
                comment=comment,
                questions=questions
            )
            return "waiting_for_info"

        except Exception as e:
            logger.error(f"❌ 发送评论失败: {e}")
            self.state.mark_processed(
                project_path, issue['iid'],
                status="failed",
                error=str(e)
            )
            return "failed"

    def _handle_can_handle(
        self,
        issue: Dict,
        project_path: str,
        project_info: Dict,
        decision: Dict
    ) -> str:
        """处理可以自动修复的情况"""
        plan = decision.get('plan', '')

        logger.info(f"📋 处理计划:\n{plan}\n")

        # 生成详细的修复指令
        instructions = self.ai.generate_fix_instructions(issue, project_info, plan)

        logger.info("🔧 生成的修复指令：")
        logger.info("="*60)
        logger.info(instructions)
        logger.info("="*60)

        # 标记为进行中
        self.state.mark_processed(
            project_path, issue['iid'],
            status="in_progress",
            plan=plan,
            instructions=instructions
        )

        logger.info("\n⚠️  需要手动执行上述操作，或集成到 CI/CD")
        logger.info("💡 未来版本将支持自动执行\n")

        return "in_progress"

    def _handle_skip(
        self,
        issue: Dict,
        project_path: str,
        decision: Dict
    ) -> str:
        """处理跳过的情况"""
        reason = decision.get('reason', '未知原因')

        logger.info(f"⏭️  跳过此 issue: {reason}\n")

        self.state.mark_processed(
            project_path, issue['iid'],
            status="skipped",
            reason=reason
        )

        return "skipped"

    def get_statistics(self) -> Dict:
        """获取处理统计"""
        return self.state.get_statistics()
