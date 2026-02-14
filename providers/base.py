"""
AI Provider 基类
定义所有 AI provider 需要实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """AI Provider 抽象基类"""

    @abstractmethod
    def analyze_issue(self, issue: Dict, project_info: Dict) -> Dict:
        """
        分析 issue 并决定如何处理

        Args:
            issue: GitLab issue 信息
            project_info: 项目信息

        Returns:
            决策字典 {
                "action": "need_info" | "can_handle" | "skip",
                "reason": "原因说明",
                "plan": "处理计划 (if can_handle)",
                "questions": ["问题列表 (if need_info)"],
                "comment": "要发送的评论"
            }
        """
        pass

    @abstractmethod
    def generate_fix_instructions(
        self,
        issue: Dict,
        project_info: Dict,
        plan: str
    ) -> str:
        """
        生成修复指令

        Args:
            issue: Issue 信息
            project_info: 项目信息
            plan: 处理计划

        Returns:
            详细的修复指令
        """
        pass
