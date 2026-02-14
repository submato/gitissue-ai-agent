"""
状态管理器
跟踪已处理的 issues，避免重复处理
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class StateManager:
    """管理 agent 的状态"""

    def __init__(self, state_file: str = "state.json"):
        """
        初始化状态管理器

        Args:
            state_file: 状态文件路径
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态文件"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "processed_issues": {},
            "last_run": None,
            "statistics": {
                "total": 0,
                "completed": 0,
                "waiting_for_info": 0,
                "in_progress": 0,
                "failed": 0
            }
        }

    def _save_state(self):
        """保存状态到文件"""
        self.state["last_run"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_issue_key(self, project_path: str, issue_iid: int) -> str:
        """
        生成 issue 唯一键

        Args:
            project_path: 项目路径 (如 "group/project")
            issue_iid: Issue IID

        Returns:
            唯一键 (如 "group/project#123")
        """
        return f"{project_path}#{issue_iid}"

    def is_processed(self, project_path: str, issue_iid: int) -> bool:
        """
        检查 issue 是否已处理

        Args:
            project_path: 项目路径
            issue_iid: Issue IID

        Returns:
            是否已处理
        """
        key = self.get_issue_key(project_path, issue_iid)
        return key in self.state["processed_issues"]

    def get_issue_status(self, project_path: str, issue_iid: int) -> Optional[str]:
        """
        获取 issue 处理状态

        Args:
            project_path: 项目路径
            issue_iid: Issue IID

        Returns:
            状态字符串或 None
        """
        key = self.get_issue_key(project_path, issue_iid)
        issue_data = self.state["processed_issues"].get(key)
        return issue_data.get("status") if issue_data else None

    def mark_processed(
        self,
        project_path: str,
        issue_iid: int,
        status: str,
        **kwargs
    ):
        """
        标记 issue 为已处理

        Args:
            project_path: 项目路径
            issue_iid: Issue IID
            status: 状态 (completed/waiting_for_info/in_progress/failed)
            **kwargs: 其他要保存的信息
        """
        key = self.get_issue_key(project_path, issue_iid)

        self.state["processed_issues"][key] = {
            "status": status,
            "processed_at": datetime.now().isoformat(),
            **kwargs
        }

        # 更新统计
        self.state["statistics"]["total"] += 1
        if status in self.state["statistics"]:
            self.state["statistics"][status] += 1

        self._save_state()

    def update_issue_status(
        self,
        project_path: str,
        issue_iid: int,
        status: str,
        **kwargs
    ):
        """
        更新 issue 状态

        Args:
            project_path: 项目路径
            issue_iid: Issue IID
            status: 新状态
            **kwargs: 要更新的其他信息
        """
        key = self.get_issue_key(project_path, issue_iid)

        if key in self.state["processed_issues"]:
            old_status = self.state["processed_issues"][key]["status"]
            self.state["processed_issues"][key].update({
                "status": status,
                "updated_at": datetime.now().isoformat(),
                **kwargs
            })

            # 更新统计
            if old_status in self.state["statistics"]:
                self.state["statistics"][old_status] -= 1
            if status in self.state["statistics"]:
                self.state["statistics"][status] += 1

            self._save_state()

    def get_statistics(self) -> Dict:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        return self.state["statistics"].copy()

    def get_all_processed_issues(self) -> Dict:
        """
        获取所有已处理的 issues

        Returns:
            已处理 issues 字典
        """
        return self.state["processed_issues"].copy()

    def clear_old_issues(self, days: int = 30):
        """
        清除旧的已处理 issues（可选功能）

        Args:
            days: 保留最近 N 天的记录
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        keys_to_remove = []

        for key, data in self.state["processed_issues"].items():
            processed_at = datetime.fromisoformat(data["processed_at"])
            if processed_at < cutoff:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.state["processed_issues"][key]

        if keys_to_remove:
            self._save_state()
