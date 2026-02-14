# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-15

### Added
- 🎉 Initial release of GitLab AI Agent
- Automatic GitLab issue analysis and processing with AI
- Multi-project support (fetch all assigned issues)
- Intelligent commenting with @mentions
- State management to avoid duplicate processing
- Dual mode operation:
  - API mode (standalone script)
  - MCP mode (Claude Code integration)
- AI Provider support:
  - Claude API (Anthropic)
  - Local proxy support
  - MCP Provider for direct execution
- MCP Tools:
  - `gitlab_fetch_issues` - Fetch assigned issues
  - `gitlab_analyze_issue` - Analyze specific issue
  - `gitlab_fix_issue` - Auto-fix with MR creation
  - `gitlab_comment` - Add comments to issues
- Management tools:
  - `manage.py` - Statistics, list issues, config
  - `process_issue.py` - Process specific issue
  - `test_components.py` - Component testing
- Complete documentation:
  - README with examples
  - Quick start guide
  - MCP setup instructions
  - Contributing guidelines
  - Demo scenarios
- Setup scripts:
  - `run.sh` - Quick start
  - `setup_mcp.sh` - Automatic MCP configuration
- GitHub Actions CI/CD pipeline

### Documentation
- Comprehensive README
- Quick start guide (QUICKSTART.md)
- MCP setup guide (docs/MCP_SETUP.md)
- Project summary (PROJECT_SUMMARY.md)
- Demo and examples (DEMO.md)
- Contributing guidelines (CONTRIBUTING.md)

### Infrastructure
- Git repository initialization
- .gitignore configuration
- MIT License
- GitHub Actions for CI/CD

## [Unreleased]

### Planned
- OpenAI Provider
- Ollama (local LLM) Provider
- Web Dashboard
- Webhook support for real-time processing
- Docker containerization
- Kubernetes deployment configs
- Multi-user support
- Advanced statistics and reporting
- Issue template matching
- Custom prompt templates
