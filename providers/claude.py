"""
Claude AI Provider
使用 Anthropic Claude API
"""

import json
import re
from typing import Dict
from anthropic import Anthropic
from .base import AIProvider


class ClaudeProvider(AIProvider):
    """Claude AI Provider"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929", api_base: str = None):
        """
        初始化 Claude Provider

        Args:
            api_key: Anthropic API key
            model: 模型名称
            api_base: API base URL (可选，用于本地代理)
        """
        self.model = model

        # 支持自定义 API base URL（用于本地代理）
        client_kwargs = {"api_key": api_key}
        if api_base:
            client_kwargs["base_url"] = api_base

        self.client = Anthropic(**client_kwargs)

    def analyze_issue(self, issue: Dict, project_info: Dict) -> Dict:
        """分析 issue"""

        prompt = self._build_analysis_prompt(issue, project_info)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            return self._parse_json_response(result_text)

        except Exception as e:
            return {
                "action": "skip",
                "reason": f"AI 分析失败: {str(e)}",
                "comment": None
            }

    def _build_analysis_prompt(self, issue: Dict, project_info: Dict) -> str:
        """构建分析提示词"""

        return f"""你是一个 GitLab issue 处理机器人。请分析以下 issue 并决定如何处理。

**项目信息**：
- 项目名称：{project_info.get('name', 'N/A')}
- 项目路径：{project_info.get('path_with_namespace', 'N/A')}
- 默认分支：{project_info.get('default_branch', 'main')}
- 描述：{project_info.get('description', 'N/A')}

**Issue 信息**：
- ID: #{issue['iid']}
- 标题：{issue['title']}
- 作者：@{issue['author']['username']}
- 标签：{', '.join(issue.get('labels', []))}
- 描述：
{issue.get('description') or '(无描述)'}

**你的任务**：
1. 分析这个 issue 是否可以自动处理
2. 如果可以处理，制定详细的处理计划
3. 如果需要更多信息，列出需要询问的具体问题
4. 如果无法处理或不适合自动化，说明原因

**返回 JSON 格式**（只返回 JSON，不要其他内容）：
{{
  "action": "need_info" | "can_handle" | "skip",
  "reason": "原因说明",
  "plan": "如果 can_handle，提供详细的处理步骤",
  "questions": ["如果 need_info，列出要问的问题"],
  "comment": "如果需要评论，提供完整的评论内容（可选）"
}}

**注意**：
- 只有明确可以自动修复的问题才返回 can_handle
- 需要人工判断或创意的任务应该 skip
- 信息不足时应该 need_info 并礼貌地询问
"""

    def _parse_json_response(self, text: str) -> Dict:
        """解析 AI 返回的 JSON"""
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass

            # 解析失败，返回 skip
            return {
                "action": "skip",
                "reason": "AI 返回格式错误",
                "comment": None
            }

    def generate_fix_instructions(
        self,
        issue: Dict,
        project_info: Dict,
        plan: str
    ) -> str:
        """生成修复指令"""

        return f"""# GitLab Issue 修复任务

## Issue 信息
- **项目**: {project_info.get('path_with_namespace')}
- **Issue**: #{issue['iid']} - {issue['title']}
- **描述**: {issue.get('description', 'N/A')}
- **作者**: @{issue['author']['username']}

## 项目信息
- **Clone URL**: {project_info.get('http_url_to_repo')}
- **默认分支**: {project_info.get('default_branch', 'main')}

## 处理计划
{plan}

## 执行步骤

1. **克隆/更新代码仓库**
   ```bash
   git clone {project_info.get('http_url_to_repo')} /tmp/workspace/{project_info.get('path')}
   cd /tmp/workspace/{project_info.get('path')}
   git checkout {project_info.get('default_branch', 'main')}
   git pull
   ```

2. **创建新分支**
   ```bash
   git checkout -b bot/issue-{issue['iid']}-fix
   ```

3. **按照计划修改代码**
   {plan}

4. **运行测试**（如果有）
   ```bash
   # 根据项目类型运行测试
   npm test || pytest || mvn test || ...
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "Fix #{issue['iid']}: {issue['title']}"
   ```

6. **推送分支**
   ```bash
   git push origin bot/issue-{issue['iid']}-fix
   ```

7. **创建 Merge Request**
   - 源分支: `bot/issue-{issue['iid']}-fix`
   - 目标分支: `{project_info.get('default_branch', 'main')}`
   - 标题: `Fix #{issue['iid']}: {issue['title']}`
   - 描述:
     ```
     Closes #{issue['iid']}

     ## 修改内容
     {plan}

     🤖 由 GitLab AI Agent 自动创建
     ```

8. **在 Issue 中评论**
   ```
   @{issue['author']['username']} 我已经创建了修复的 MR: [MR链接]

   请审查修改内容。如果有问题请告诉我。

   🤖 GitLab AI Agent
   ```
"""
