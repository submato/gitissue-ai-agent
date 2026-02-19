# Quick Setup Guide - Complete GitHub Automation

## 🎯 Current Status
All features are implemented and tested. The only remaining step is uploading the workflow file to GitHub.

## ⚡ Complete Setup in 3 Steps

### Step 1: Upload Workflow File to GitHub

**Via Web Interface (Easiest):**

1. Open this URL in your browser:
   ```
   https://github.com/submato/gitissue-ai-agent/new/main
   ```

2. In the "Name your file..." field, type:
   ```
   .github/workflows/issue-agent.yml
   ```

3. Copy and paste this content:

```yaml
name: Issue AI Agent

on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]

jobs:
  process-issue:
    # 只在issue有 'bot' 标签时运行
    if: contains(github.event.issue.labels.*.name, 'bot')
    runs-on: ubuntu-latest

    permissions:
      issues: write
      contents: write
      pull-requests: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Process issue with AI agent
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ISSUE_NUMBER: ${{ github.event.issue.number }}
          REPO_OWNER: ${{ github.repository_owner }}
          REPO_NAME: ${{ github.event.repository.name }}
        run: |
          python process_github_issue.py

      - name: Add processing label
        if: success()
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['processing']
            });
```

4. Click "Commit new file"

### Step 2: Add API Key Secret

1. Go to repository settings:
   ```
   https://github.com/submato/gitissue-ai-agent/settings/secrets/actions
   ```

2. Click "New repository secret"

3. Set:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Secret**: Your Claude API key from https://console.anthropic.com/settings/keys

4. Click "Add secret"

### Step 3: Test It!

1. Create a new issue in your repository
2. Add the `bot` label to it
3. Watch the magic happen! ✨

Within seconds, you'll see:
- 🤖 "AI Agent 已开始处理此 issue，请稍等..." comment
- Analysis and response from the AI
- Automatic label updates

## 🔄 Interactive Testing

After the initial response, try:
1. Reply to the issue with additional information
2. Watch the agent detect your comment and re-analyze
3. See how it adjusts its response based on your input

## 📊 Example Workflow

**You create issue**: "增加docker部署的方式"
**Agent responds**: "需要更多信息" + asks specific questions
**You reply**: "用最简单的方式"
**Agent re-analyzes**: "可以处理" + provides implementation plan

## 🆘 Troubleshooting

If the workflow doesn't trigger:
1. Check the "Actions" tab in your repository
2. Ensure the workflow file was created correctly
3. Verify the `ANTHROPIC_API_KEY` secret is set
4. Ensure the issue has the 'bot' label

## 📝 Alternative: Update Git Token

If you prefer to push the workflow file via git:

1. Create new GitHub token with 'workflow' scope:
   - https://github.com/settings/tokens/new
   - Enable: `repo`, `workflow`

2. Update git remote:
   ```bash
   git remote set-url origin https://<NEW_TOKEN>@github.com/submato/gitissue-ai-agent.git
   ```

3. Push:
   ```bash
   git push origin main
   ```

## ✅ What's Already Done

- ✅ GitHub API client (`core/github.py`)
- ✅ Issue processor (`process_github_issue.py`)
- ✅ Comment monitoring support
- ✅ Context-aware AI analysis
- ✅ Immediate feedback system
- ✅ Local logging
- ✅ Workflow file (created locally)
- ✅ Complete documentation

All code is ready - just need the workflow file on GitHub!

## 🎉 That's It!

Once you complete these 3 steps, your repository will have fully automated AI-powered issue processing.
