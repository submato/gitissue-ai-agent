"""
GitLab API 客户端
负责所有与 GitLab 的交互
"""

import requests
from typing import List, Dict, Optional
from urllib.parse import quote


class GitLabClient:
    """GitLab API 客户端"""

    def __init__(self, url: str, token: str):
        """
        初始化 GitLab 客户端

        Args:
            url: GitLab 实例 URL (如 https://gitlab.com)
            token: Personal Access Token
        """
        self.base_url = url.rstrip('/')
        self.token = token
        self.headers = {"PRIVATE-TOKEN": token}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_assigned_issues(
        self,
        username: str,
        labels: Optional[List[str]] = None,
        state: str = "opened"
    ) -> List[Dict]:
        """
        获取分配给特定用户的所有 issues（跨项目）

        Args:
            username: GitLab 用户名
            labels: 过滤标签列表
            state: issue 状态 (opened/closed)

        Returns:
            issues 列表
        """
        url = f"{self.base_url}/api/v4/issues"
        params = {
            "assignee_username": username,
            "state": state,
            "scope": "all"
        }

        if labels:
            params["labels"] = ",".join(labels)

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_project_info(self, project_id: str) -> Dict:
        """
        获取项目信息

        Args:
            project_id: 项目 ID 或 path (需要 URL 编码)

        Returns:
            项目信息字典
        """
        # URL 编码项目路径
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def add_comment(self, project_id: str, issue_iid: int, body: str) -> Dict:
        """
        在 issue 上添加评论

        Args:
            project_id: 项目 ID
            issue_iid: Issue IID (项目内的 ID)
            body: 评论内容

        Returns:
            评论信息
        """
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}/issues/{issue_iid}/notes"
        data = {"body": body}

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def create_merge_request(
        self,
        project_id: str,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str
    ) -> Dict:
        """
        创建 Merge Request

        Args:
            project_id: 项目 ID
            source_branch: 源分支
            target_branch: 目标分支
            title: MR 标题
            description: MR 描述

        Returns:
            MR 信息
        """
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}/merge_requests"
        data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_issue_by_id(self, project_id: str, issue_iid: int) -> Dict:
        """
        获取特定 issue 的详细信息

        Args:
            project_id: 项目 ID
            issue_iid: Issue IID

        Returns:
            Issue 详细信息
        """
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}/issues/{issue_iid}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def update_issue_labels(
        self,
        project_id: str,
        issue_iid: int,
        labels: List[str]
    ) -> Dict:
        """
        更新 issue 标签

        Args:
            project_id: 项目 ID
            issue_iid: Issue IID
            labels: 新的标签列表

        Returns:
            更新后的 issue 信息
        """
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}/issues/{issue_iid}"
        data = {"labels": ",".join(labels)}

        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def close_issue(self, project_id: str, issue_iid: int) -> Dict:
        """
        关闭 issue

        Args:
            project_id: 项目 ID
            issue_iid: Issue IID

        Returns:
            更新后的 issue 信息
        """
        encoded_id = quote(project_id, safe='')
        url = f"{self.base_url}/api/v4/projects/{encoded_id}/issues/{issue_iid}"
        data = {"state_event": "close"}

        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()
