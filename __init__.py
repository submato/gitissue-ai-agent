"""
GitLab AI Agent
自动处理 GitLab issues 的 AI agent 框架
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from .core.gitlab import GitLabClient
from .core.agent import IssueAgent
from .core.state import StateManager

__all__ = ["GitLabClient", "IssueAgent", "StateManager"]
