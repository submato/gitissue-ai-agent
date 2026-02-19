"""
GitHub API 客户端
负责所有与 GitHub 的交互
"""

import requests
from typing import List, Dict, Optional


class GitHubClient:
    """GitHub API 客户端"""

    def __init__(self, token: str, repo_owner: str = None, repo_name: str = None):
        """
        初始化 GitHub 客户端

        Args:
            token: Personal Access Token
            repo_owner: 仓库所有者（可选，用于特定仓库操作）
            repo_name: 仓库名称（可选，用于特定仓库操作）
        """
        self.base_url = "https://api.github.com"
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_repository_issues(
        self,
        owner: str = None,
        repo: str = None,
        labels: Optional[List[str]] = None,
        state: str = "open",
        assignee: str = None
    ) -> List[Dict]:
        """
        获取仓库的 issues

        Args:
            owner: 仓库所有者（默认使用初始化时的值）
            repo: 仓库名称（默认使用初始化时的值）
            labels: 过滤标签列表
            state: issue 状态 (open/closed/all)
            assignee: 分配给的用户（可选）

        Returns:
            issues 列表
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state}

        if labels:
            params["labels"] = ",".join(labels)

        if assignee:
            params["assignee"] = assignee

        response = self.session.get(url, params=params)
        response.raise_for_status()

        # 过滤掉 pull requests（GitHub API 将 PR 也作为 issue 返回）
        issues = response.json()
        return [issue for issue in issues if "pull_request" not in issue]

    def get_issue_by_number(
        self,
        issue_number: int,
        owner: str = None,
        repo: str = None
    ) -> Dict:
        """
        获取特定 issue 的详细信息

        Args:
            issue_number: Issue 编号
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            Issue 详细信息
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def add_comment(
        self,
        issue_number: int,
        body: str,
        owner: str = None,
        repo: str = None
    ) -> Dict:
        """
        在 issue 上添加评论

        Args:
            issue_number: Issue 编号
            body: 评论内容
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            评论信息
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        data = {"body": body}

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def add_labels(
        self,
        issue_number: int,
        labels: List[str],
        owner: str = None,
        repo: str = None
    ) -> List[Dict]:
        """
        为 issue 添加标签

        Args:
            issue_number: Issue 编号
            labels: 要添加的标签列表
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            标签列表
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels"
        data = {"labels": labels}

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def remove_label(
        self,
        issue_number: int,
        label: str,
        owner: str = None,
        repo: str = None
    ) -> None:
        """
        从 issue 移除标签

        Args:
            issue_number: Issue 编号
            label: 要移除的标签
            owner: 仓库所有者
            repo: 仓库名称
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}"

        response = self.session.delete(url)
        response.raise_for_status()

    def update_issue_labels(
        self,
        issue_number: int,
        labels: List[str],
        owner: str = None,
        repo: str = None
    ) -> List[Dict]:
        """
        更新 issue 标签（替换所有标签）

        Args:
            issue_number: Issue 编号
            labels: 新的标签列表
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            标签列表
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/labels"
        data = {"labels": labels}

        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response.json()

    def create_pull_request(
        self,
        title: str,
        head: str,
        base: str,
        body: str = "",
        owner: str = None,
        repo: str = None
    ) -> Dict:
        """
        创建 Pull Request

        Args:
            title: PR 标题
            head: 源分支名称
            base: 目标分支名称
            body: PR 描述
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            PR 信息
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }

        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def close_issue(
        self,
        issue_number: int,
        owner: str = None,
        repo: str = None
    ) -> Dict:
        """
        关闭 issue

        Args:
            issue_number: Issue 编号
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            更新后的 issue 信息
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        data = {"state": "closed"}

        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_repository_info(
        self,
        owner: str = None,
        repo: str = None
    ) -> Dict:
        """
        获取仓库信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库信息字典
        """
        owner = owner or self.repo_owner
        repo = repo or self.repo_name

        if not owner or not repo:
            raise ValueError("Must provide owner and repo")

        url = f"{self.base_url}/repos/{owner}/{repo}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
