# Workflow File for Manual Addition

If automated push fails due to token permissions, manually add this file to GitHub:

**File path**: `.github/workflows/issue-agent.yml`

**Instructions**:
1. Go to: https://github.com/YOUR_USERNAME/gitissue-ai-agent/new/main
2. In the filename field, type: `.github/workflows/issue-agent.yml`
3. Copy and paste the content below
4. Click "Commit new file"

**File content**:

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

After adding the workflow file, remember to:
1. Add `ANTHROPIC_API_KEY` secret in repository settings
2. See [GitHub Actions Setup Guide](GITHUB_ACTIONS_SETUP.md) for details
