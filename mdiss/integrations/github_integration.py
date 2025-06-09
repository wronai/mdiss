"""GitHub integration for issue management."""
import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from github import Github, GithubIntegration
from github.Issue import Issue
from github.Repository import Repository


class GitHubIntegration:
    """Handles GitHub API interactions for issue management."""

    def __init__(
        self,
        token: Optional[str] = None,
        app_id: Optional[str] = None,
        private_key: Optional[str] = None,
        org_name: Optional[str] = None,
    ):
        """Initialize GitHub integration.

        Args:
            token: GitHub personal access token
            app_id: GitHub App ID (for app authentication)
            private_key: GitHub App private key (for app authentication)
            org_name: Organization name (required for app authentication)
        """
        load_dotenv()
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.app_id = app_id or os.getenv("GITHUB_APP_ID")
        self.private_key = private_key or os.getenv("GITHUB_PRIVATE_KEY")
        self.org_name = org_name or os.getenv("GITHUB_ORG")
        self.client = self._get_client()

    def _get_client(self) -> Union[Github, GithubIntegration]:
        """Initialize and return GitHub client."""
        if self.app_id and self.private_key and self.org_name:
            # App authentication
            integration = GithubIntegration(
                integration_id=self.app_id, private_key=self.private_key
            )
            installation_id = integration.get_installations()[0].id
            return integration.get_github_for_installation(installation_id)

        if self.token:
            # Token authentication
            return Github(self.token)

        raise ValueError(
            "Either GitHub token or App credentials (app_id, private_key, org_name) are required."
        )

    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new GitHub issue.

        Args:
            repo_name: Repository name with owner (e.g., 'owner/repo')
            title: Issue title
            body: Issue body (markdown supported)
            labels: List of label names
            **kwargs: Additional GitHub issue attributes

        Returns:
            Created issue data
        """
        repo = self.client.get_repo(repo_name)
        issue = repo.create_issue(title=title, body=body, labels=labels or [], **kwargs)
        return self._issue_to_dict(issue)

    def update_issue(
        self, repo_name: str, issue_number: int, **kwargs: Any
    ) -> Dict[str, Any]:
        """Update an existing issue.

        Args:
            repo_name: Repository name with owner
            issue_number: Issue number
            **kwargs: Fields to update

        Returns:
            Updated issue data
        """
        repo = self.client.get_repo(repo_name)
        issue = repo.get_issue(issue_number)

        # Update fields if provided
        for key, value in kwargs.items():
            if hasattr(issue, key):
                setattr(issue, f"_{key}", value)

        issue = issue.edit(**kwargs)
        return self._issue_to_dict(issue)

    def list_issues(
        self, repo_name: str, state: str = "open", **filters: Any
    ) -> List[Dict[str, Any]]:
        """List issues in a repository.

        Args:
            repo_name: Repository name with owner
            state: Issue state ('open', 'closed', 'all')
            **filters: Additional GitHub issue filters

        Returns:
            List of issues
        """
        repo = self.client.get_repo(repo_name)
        issues = repo.get_issues(state=state, **filters)
        return [self._issue_to_dict(issue) for issue in issues]

    @staticmethod
    def _issue_to_dict(issue: Issue) -> Dict[str, Any]:
        """Convert GitHub Issue object to dictionary."""
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "labels": [label.name for label in issue.labels],
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "url": issue.html_url,
            "user": issue.user.login if issue.user else None,
            "assignees": [assignee.login for assignee in issue.assignees],
        }
