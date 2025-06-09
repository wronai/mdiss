# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-06-09

### Added
- ✨ Initial release of mdiss
- 🚀 Automated GitHub issue generation from markdown files
- 📊 Intelligent error analysis and categorization
- 🎯 Priority assignment based on error types
- 💡 Automatic solution suggestions
- 🔧 Rich CLI interface with multiple commands
- 🧪 Dry run mode for testing
- 📤 Export functionality (JSON, CSV, table)
- 🔐 Secure GitHub token management
- 📋 Issue management (list, check existing)
- 🏷️ Smart labeling system
- 📖 Comprehensive markdown parser
- 🧪 100% test coverage
- 📚 Complete documentation

### Features
- **Core Functionality**
  - Parse markdown files with failed commands
  - Analyze errors and determine priorities/categories
  - Generate GitHub issues with detailed descriptions
  - Suggest solutions based on error types
  
- **CLI Commands**
  - `mdiss create` - Create GitHub issues
  - `mdiss analyze` - Analyze markdown files
  - `mdiss list-issues` - List repository issues
  - `mdiss export` - Export data to various formats
  - `mdiss setup` - Interactive configuration

- **Error Categories**
  - `dependencies` - Package/dependency issues
  - `missing-files` - File not found errors
  - `permissions` - Permission/access errors
  - `timeout` - Command timeout errors
  - `syntax` - Syntax/parsing errors
  - `configuration` - Config file issues
  - `build-failure` - General build failures

- **Priority Levels**
  - `CRITICAL` - System crashes, segfaults
  - `HIGH` - Timeouts, dependency issues
  - `MEDIUM` - Standard errors, missing files
  - `LOW` - Minor issues

### Technical Details
- **Dependencies**
  - `requests` - GitHub API communication
  - `click` - CLI framework
  - `rich` - Rich terminal output
  - `pydantic` - Data validation

- **Development Tools**
  - `pytest` - Testing framework
  - `black` - Code formatting
  - `isort` - Import sorting
  - `flake8` - Linting
  - `mypy` - Type checking
  - `pre-commit` - Git hooks

### Supported Formats
- Input: Markdown files with specific command failure format
- Output: GitHub issues, JSON, CSV, tables
- Token storage: Local files, environment variables

### Examples
```bash
# Quick start
mdiss setup
mdiss analyze failures.md
mdiss create failures.md owner repo --dry-run

# Advanced usage
mdiss create failures.md owner repo \
  --assignees "dev1,dev2" \
  --milestone 5 \
  --skip-existing
```

### Architecture
- **Parser**: Regex-based markdown parsing
- **Analyzer**: Rule-based error categorization
- **Client**: GitHub API integration
- **CLI**: Click-based command interface
- **Models**: Pydantic data structures

### Quality Metrics
- 🧪 100% test coverage
- 📊 Type hints throughout
- 🔍 Comprehensive linting
- 📖 Full documentation
- 🚀 CI/CD pipeline

### Performance
- Fast markdown parsing with compiled regex
- Efficient GitHub API usage with session reuse
- Minimal dependencies for quick installation
- Batch processing for multiple issues

## [Unreleased]

### Planned Features
- 🔄 Support for other issue trackers (GitLab, Jira)
- 📈 Advanced analytics and reporting
- 🤖 AI-powered error analysis
- 🔌 Plugin system for custom analyzers
- 📱 Web interface
- 🚀 GitHub Actions integration
- 📊 Dashboard for issue tracking
- 🔍 Search and filter capabilities

### Roadmap
- **v1.1.x** - GitLab support
- **v1.2.x** - Advanced analytics
- **v1.3.x** - AI integration
- **v2.0.x** - Plugin system

---

**Note**: This changelog follows [semantic versioning](https://semver.org/). 
For migration guides and breaking changes, see [UPGRADING.md](UPGRADING.md).