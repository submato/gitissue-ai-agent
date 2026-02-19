# GitHub Actions Setup Guide

This guide explains how to enable automated issue processing using GitHub Actions.

## Prerequisites

- Repository hosted on GitHub
- Anthropic API key (or local proxy URL)

## Setup Steps

### 1. Add Workflow File

The workflow file is already in this repository at `.github/workflows/issue-agent.yml`.

If you need to add it manually:

1. Go to your repository on GitHub
2. Click "Add file" → "Create new file"
3. Enter filename: `.github/workflows/issue-agent.yml`
4. Copy the content from `.github/workflows/issue-agent.yml` in this repo
5. Commit the file

### 2. Add API Key Secret

1. Go to your repository's Settings
2. Navigate to: **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add the following secret:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Value**: Your Anthropic API key (or "any-value" if using local proxy)
5. Click **"Add secret"**

### 3. Test the Workflow

1. Create a new issue in your repository
2. Add the `bot` label to the issue
3. The workflow will automatically:
   - Detect the labeled issue
   - Analyze it with AI
   - Post a comment with analysis
   - Update labels based on the result

## How It Works

When an issue is opened or labeled with `bot`:

1. **GitHub Actions triggers** the workflow
2. **Agent analyzes** the issue using Claude AI
3. **Agent decides** the action:
   - `need_info` → Asks questions in comments, adds `needs-info` label
   - `can_handle` → Plans the fix, adds `in-progress` label
   - `skip` → Explains why it can't help, adds `cannot-fix` label
4. **Labels updated** automatically to track status

## Monitoring

View workflow runs:
- Go to **Actions** tab in your repository
- Click on "Issue AI Agent" workflow
- See detailed logs for each run

## Troubleshooting

### Workflow not triggering

- Ensure the workflow file is in `.github/workflows/` directory
- Check that the issue has the `bot` label
- Verify in Actions tab if workflow is enabled

### API errors

- Check that `ANTHROPIC_API_KEY` secret is set correctly
- If using local proxy, update the `api_base` in `process_github_issue.py`

### Permission errors

The workflow has the following permissions:
```yaml
permissions:
  issues: write
  contents: write
  pull-requests: write
```

These are required for the agent to:
- Read issues
- Post comments
- Update labels
- Create pull requests (future feature)

## Local Testing

You can test the agent locally without GitHub Actions:

```bash
GITHUB_TOKEN=$(gh auth token) \
ANTHROPIC_API_KEY="your-api-key" \
ISSUE_NUMBER=1 \
REPO_OWNER="your-username" \
REPO_NAME="your-repo" \
python3 process_github_issue.py
```

This will process the specified issue and show you the results.

## Next Steps

After setup is complete, your repository will automatically process issues with the `bot` label!

Try it out:
1. Create an issue
2. Add `bot` label
3. Watch the magic happen! ✨
