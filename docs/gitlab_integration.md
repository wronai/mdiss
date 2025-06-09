# GitLab Integration Guide

This guide explains how to use the GitLab integration in mdiss for managing issues and merge requests programmatically.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [Basic Usage](#basic-usage)
- [Working with Issues](#working-with-issues)
- [Working with Merge Requests](#working-with-merge-requests)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. Python 3.9 or higher
2. mdiss installed with GitLab support
3. GitLab account with appropriate permissions
4. Personal Access Token with `api` scope

## Authentication

### Environment Variables

Set these environment variables in your shell or `.env` file:

```bash
# Required
export GITLAB_TOKEN="your-gitlab-token"

# Optional: For self-hosted GitLab instances
export GITLAB_URL="https://gitlab.com"  # Default
```

### Initialize GitLab Integration

```python
from mdiss.integrations.gitlab_integration import GitLabIntegration

# Using environment variables
gitlab = GitLabIntegration()

# Or explicitly provide credentials
gitlab = GitLabIntegration(
    token="your-gitlab-token",
    url="https://gitlab.com"  # Optional, defaults to GitLab.com
)
```

## Basic Usage

### List Projects

```python
# List all accessible projects
projects = gitlab.list_projects()
for project in projects:
    print(f"{project.name}: {project.web_url}")

# Filter projects by search term
projects = gitlab.list_projects(search="mdiss")
```

### Get Project by ID or Path

```python
# By project ID
project = gitlab.get_project(12345678)

# By path with namespace
project = gitlab.get_project("username/myrepo")
```

## Working with Issues

### Create an Issue

```python
issue = gitlab.create_issue(
    project_id="username/myrepo",
    title="Bug: Login page not loading",
    description="The login page shows a 500 error when accessed from mobile devices.",
    labels=["bug", "priority:high"],
    assignee_ids=[42],  # User ID of the assignee
    milestone_id=1,     # Optional milestone ID
    due_date="2024-12-31"
)
print(f"Created issue: {issue.web_url}")
```

### List Issues

```python
# List all issues in a project
issues = gitlab.list_issues("username/myrepo")

# Filter issues
issues = gitlab.list_issues(
    project_id="username/myrepo",
    state="opened",
    labels=["bug"],
    assignee_id=42
)
```

### Update an Issue

```python
updated_issue = gitlab.update_issue(
    project_id="username/myrepo",
    issue_iid=123,
    title="Updated: Login page not loading",
    description="Additional details...",
    state_event="close"
)
```

## Working with Merge Requests

### Create a Merge Request

```python
mr = gitlab.create_merge_request(
    project_id="username/myrepo",
    source_branch="feature/login-fix",
    target_branch="main",
    title="Fix login page issues",
    description="## Changes\n- Fixed 500 error on login page\n- Improved mobile layout",
    labels=["frontend", "bugfix"]
)
print(f"Created MR: {mr.web_url}")
```

### List Merge Requests

```python
# List all MRs in a project
mrs = gitlab.list_merge_requests("username/myrepo")

# Filter MRs
mrs = gitlab.list_merge_requests(
    project_id="username/myrepo",
    state="opened",
    author_id=42
)
```

## Advanced Usage

### Custom API Calls

For features not covered by the wrapper, you can access the underlying `python-gitlab` client:

```python
# Get the raw client
client = gitlab.client

# Make direct API calls
project = client.projects.get("username/myrepo")
for branch in project.branches.list():
    print(branch.name)
```

### Error Handling

```python
from gitlab.exceptions import GitlabError

try:
    issue = gitlab.create_issue(
        project_id="nonexistent/repo",
        title="Test",
        description="Test"
    )
except GitlabError as e:
    print(f"GitLab API error: {e.error_message}")
    if e.response_code == 404:
        print("Project not found")
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your GitLab token has the correct scopes (`api` scope required)
   - Check token expiration
   - For self-hosted instances, ensure the correct URL is set

2. **Project Not Found**
   - Verify the project exists and is accessible with your token
   - Check for typos in the project path/ID

3. **Rate Limiting**
   - Implement retry logic for rate-limited requests
   - Consider using a token with higher rate limits

### Debugging

Enable debug logging to see API requests:

```python
import logging
import gitlab

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('gitlab').setLevel(logging.DEBUG)
```

### Getting Help

- [GitLab API Documentation](https://docs.gitlab.com/ee/api/)
- [python-gitlab Documentation](https://python-gitlab.readthedocs.io/)
- [Open an issue](https://github.com/wronai/mdiss/issues) for mdiss-specific problems
