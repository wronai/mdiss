"""GitLab integration for issue management."""
import os
from typing import Any, Dict, List, Optional

import gitlab
from dotenv import load_dotenv


class GitLabIntegration:
    """Handles GitLab API interactions for issue management."""

    def __init__(self, token: Optional[str] = None, url: Optional[str] = None):
        """Initialize GitLab integration.

        Args:
            token: GitLab private token with API access
            url: GitLab instance URL (defaults to gitlab.com)
        """
        load_dotenv()
        self.token = token or os.getenv("GITLAB_TOKEN")
        self.url = url or os.getenv("GITLAB_URL", "https://gitlab.com")
        self.client = self._get_client()

    def _get_client(self) -> gitlab.Gitlab:
        """Initialize and return GitLab client."""
        if not self.token:
            raise ValueError(
                "GitLab token is required. Set GITLAB_TOKEN environment variable."
            )
        return gitlab.Gitlab(self.url, private_token=self.token)

    def create_issue(
        self,
        project_id: str,
        title: str,
        description: str,
        labels: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new issue in GitLab.

        Args:
            project_id: Project ID or path with namespace
            title: Issue title
            description: Issue description (markdown supported)
            labels: List of labels to apply
            **kwargs: Additional GitLab issue attributes

        Returns:
            Created issue data
        """
        project = self.client.projects.get(project_id)
        issue = project.issues.create(
            {
                "title": title,
                "description": description,
                "labels": labels or [],
                **kwargs,
            }
        )
        return issue.attributes

    def update_issue(
        self, project_id: str, issue_iid: int, **kwargs: Any
    ) -> Dict[str, Any]:
        """Update an existing issue.

        Args:
            project_id: Project ID or path with namespace
            issue_iid: Issue IID (not the same as ID)
            **kwargs: Fields to update

        Returns:
            Updated issue data
        """
        issue = self.client.projects.get(project_id).issues.get(issue_iid)
        for key, value in kwargs.items():
            setattr(issue, key, value)
        issue.save()
        return issue.attributes

    def list_issues(
        self, project_id: str, state: str = "opened", **filters: Any
    ) -> List[Dict[str, Any]]:
        """List issues in a project.

        Args:
            project_id: Project ID or path with namespace
            state: Issue state ('opened', 'closed', 'all')
            **filters: Additional GitLab issue filters

        Returns:
            List of issues
        """
        project = self.client.projects.get(project_id)
        issues = project.issues.list(state=state, **filters)
        return [issue.attributes for issue in issues]
