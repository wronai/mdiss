"""
GitHub API client for interacting with GitHub's REST API.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException

from .models import FailedCommand, AnalysisResult


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""
    title: str
    body: str
    labels: List[str] = None
    assignees: List[str] = None
    milestone: int = None
    state: str = 'open'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary for API requests."""
        return {
            'title': self.title,
            'body': self.body,
            'labels': self.labels or [],
            'assignees': self.assignees or [],
            'milestone': self.milestone,
            'state': self.state
        }


class GitHubClient:
    """Client for interacting with the GitHub API."""
    
    BASE_URL = 'https://api.github.com'
    
    def __init__(self, config=None, token: Optional[str] = None, **kwargs):
        """
        Initialize the GitHub client.
        
        Args:
            config: Optional GitHubConfig object with token, owner, and repo
            token: GitHub personal access token (alternative to config)
            **kwargs: Additional arguments like base_url for GitHub Enterprise
        """
        self.config = config
        
        # Status mapping for better user experience
        self.status_mapping = {
            'open': {'state': 'open'},
            'closed': {'state': 'closed'},
            'in_progress': {'state': 'open', 'labels': ['in progress']},
            'reopened': {'state': 'open'},
            'done': {'state': 'closed', 'labels': ['done']}
        }
        
        if config:
            self.token = config.token
            self._default_owner = config.owner
            self._default_repo = config.repo
        else:
            self.token = token or os.getenv('GITHUB_TOKEN')
            self._default_owner = None
            self._default_repo = None
            
        self.base_url = kwargs.get('base_url', self.BASE_URL)
        self.session = requests.Session()
        self._setup_session()
        
    def _get_owner_repo(self, owner: Optional[str] = None, repo: Optional[str] = None) -> tuple:
        """Get owner and repo, falling back to config if not provided."""
        owner = owner or self._default_owner
        repo = repo or self._default_repo
        
        if not owner or not repo:
            raise ValueError("Owner and repo must be provided or set in config")
            
        return owner, repo
    
    @classmethod
    def setup_token(cls) -> str:
        """Interactively set up GitHub token.
        
        Returns:
            The configured token
            
        Raises:
            ValueError: If no token is provided
        """
        import webbrowser
        import getpass
        
        print("Please create a GitHub personal access token with 'repo' scope")
        print("You can create one at: https://github.com/settings/tokens/new")
        
        webbrowser.open("https://github.com/settings/tokens/new")
        
        token = getpass.getpass("Enter your GitHub personal access token: ")
        if not token:
            raise ValueError("Token cannot be empty")
            
        return token
        
    def set_config(self, config) -> None:
        """Update the GitHub configuration.
        
        Args:
            config: The new GitHub configuration
        """
        self.config = config
        self.token = config.token
        self._default_owner = config.owner
        self._default_repo = config.repo
        self._setup_session()
        
    def test_connection(self) -> bool:
        """Test the connection to GitHub API.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        if not self.config:
            return False
            
        try:
            response = self.session.get(
                f"{self.base_url}/repos/{self.config.owner}/{self.config.repo}"
            )
            return response.status_code == 200
        except RequestException:
            return False
            
    def _create_title(self, command: 'FailedCommand') -> str:
        """Create a title for a failed command issue.
        
        Args:
            command: The failed command
            
        Returns:
            str: The formatted title
        """
        return f"Fix failed command: {command.title}"
        
    def _create_labels(self, command: 'FailedCommand', analysis: 'AnalysisResult') -> List[str]:
        """Create labels for a failed command issue.
        
        Args:
            command: The failed command
            analysis: The analysis result
            
        Returns:
            List of label names
        """
        labels = ["bug", "automated"]
        
        # Add priority label
        if hasattr(analysis, 'priority') and analysis.priority:
            labels.append(f"priority:{analysis.priority.value}")
            
        # Add category label
        if hasattr(analysis, 'category') and analysis.category:
            labels.append(f"category:{analysis.category.value}")
            
        return labels
        
    def get_repository_info(self) -> Dict[str, Any]:
        """Get information about the configured repository.
        
        Returns:
            Dictionary with repository information
            
        Raises:
            ValueError: If no repository configuration is available
            RequestException: If the request fails
        """
        if not self.config:
            raise ValueError("No repository configuration available")
            
        return self._request(
            'get',
            f'/repos/{self.config.owner}/{self.config.repo}'
        )
        
    def _setup_session(self):
        """Set up the requests session with headers and auth."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'mdiss/1.0.60',  # Updated to match test expectation
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        self.session.headers.update(headers)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a request to the GitHub API.
        
        Args:
            method: HTTP method (get, post, patch, etc.)
            endpoint: API endpoint (e.g., '/repos/owner/repo/issues')
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            RequestException: If the request fails
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg = f"{e}: {error_details.get('message', 'Unknown error')}"
                except ValueError:
                    error_msg = f"{e}: {e.response.text}"
            raise RequestException(f"GitHub API request failed: {error_msg}") from e
    
    def create_issue(
        self, 
        owner: Optional[str] = None, 
        repo: Optional[str] = None,
        issue: Optional[Union[GitHubIssue, Dict[str, Any]]] = None,
        **issue_data
    ) -> Dict[str, Any]:
        """
        Create a new GitHub issue.
        
        Args:
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            issue: GitHubIssue instance or dict with issue data
            **issue_data: Issue data as keyword arguments (alternative to issue parameter)
            
        Returns:
            Created issue data
        """
        owner, repo = self._get_owner_repo(owner, repo)
        
        if issue is not None:
            if isinstance(issue, GitHubIssue):
                issue_data = issue.to_dict()
            else:
                issue_data = issue
        
        endpoint = f'/repos/{owner}/{repo}/issues'
        return self._request('post', endpoint, json=issue_data)
    
    def create_issue_from_failed_command(
        self,
        failed_command: FailedCommand,
        analysis: AnalysisResult,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue from a failed command and its analysis.
        
        Args:
            failed_command: The failed command
            analysis: Analysis of the failed command
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            **kwargs: Additional issue parameters
            
        Returns:
            Created issue data
        """
        owner, repo = self._get_owner_repo(owner, repo)
        
        title = f"Failed command: {failed_command.command[:100]}"
        
        # Format the issue body with markdown
        body = (
            f"## Failed Command\n"
            f"```\n{failed_command.command}\n```\n\n"
            f"## Error Output\n"
            f"```\n{failed_command.output}\n```\n\n"
            f"## Analysis\n"
            f"- **Priority:** {analysis.priority.value}\n"
            f"- **Category:** {analysis.category.value}\n"
            f"- **Root Cause:** {analysis.root_cause or 'Unknown'}\n\n"
            f"## Suggested Solution\n{analysis.suggested_solution or 'No specific solution provided.'}"
        )
        
        # Create labels based on priority and category
        labels = [
            f"priority:{analysis.priority.value}",
            f"category:{analysis.category.value}",
            "bug"
        ]
        
        # Include any additional labels from kwargs
        if 'labels' in kwargs:
            if isinstance(kwargs['labels'], str):
                labels.append(kwargs.pop('labels'))
            else:
                labels.extend(kwargs.pop('labels', []))
        
        issue = GitHubIssue(
            title=title,
            body=body,
            labels=labels,
            **kwargs
        )
        
        return self.create_issue(owner, repo, issue)
    
    def get_issue(
        self,
        issue_number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a single issue.
        
        Args:
            issue_number: Issue number
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            
        Returns:
            Issue data
        """
        owner, repo = self._get_owner_repo(owner, repo)
        endpoint = f'/repos/{owner}/repo/issues/{issue_number}'
        return self._request('get', endpoint)
    
    def list_issues(
        self, 
        state: str = 'open',
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        **params
    ) -> List[Dict[str, Any]]:
        """
        List repository issues.
        
        Args:
            state: Issue state (open, closed, all)
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            **params: Additional query parameters
            
        Returns:
            List of issues
        """
        owner, repo = self._get_owner_repo(owner, repo)
        params['state'] = state
        endpoint = f'/repos/{owner}/{repo}/issues'
        return self._request('get', endpoint, params=params)
    
    def update_issue(
        self, 
        issue_number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        **updates
    ) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            issue_number: Issue number
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            **updates: Fields to update
            
        Returns:
            Updated issue data
        """
        owner, repo = self._get_owner_repo(owner, repo)
        endpoint = f'/repos/{owner}/{repo}/issues/{issue_number}'
        return self._request('patch', endpoint, json=updates)
    
    def close_issue(
        self,
        issue_number: int,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close an issue.
        
        Args:
            issue_number: Issue number
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            
        Returns:
            Updated issue data
        """
        return self.update_issue(issue_number, owner=owner, repo=repo, state='closed')
        
    def update_issue_status(
        self,
        issue_number: int,
        status: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of an issue with a user-friendly status name.
        
        Args:
            issue_number: The issue number to update
            status: The new status (open, closed, in_progress, reopened, done)
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            
        Returns:
            Updated issue data
            
        Raises:
            ValueError: If the status is invalid
            RequestException: If the API request fails
        """
        status = status.lower()
        if status not in self.status_mapping:
            valid_statuses = "', '".join(self.status_mapping.keys())
            raise ValueError(f"Invalid status: '{status}'. Must be one of: '{valid_statuses}'")
            
        # Get the status configuration
        status_config = self.status_mapping[status]
        update_data = {}
        
        # Get current issue to preserve existing labels
        current_issue = self.get_issue(issue_number, owner=owner, repo=repo)
        if not current_issue:
            raise RequestException(f"Issue #{issue_number} not found")
            
        # Handle state update
        if 'state' in status_config:
            update_data['state'] = status_config['state']
            
        # Handle labels
        if 'labels' in status_config:
            current_labels = {label['name'] for label in current_issue.get('labels', [])}
            
            # Remove any existing status-related labels
            status_labels = set()
            for config in self.status_mapping.values():
                if 'labels' in config:
                    if isinstance(config['labels'], list):
                        status_labels.update(config['labels'])
                    else:
                        status_labels.add(config['labels'])
            
            # Keep only non-status labels
            new_labels = [label for label in current_labels if label not in status_labels]
            
            # Add new status labels if any
            if 'labels' in status_config:
                if isinstance(status_config['labels'], list):
                    new_labels.extend(status_config['labels'])
                else:
                    new_labels.append(status_config['labels'])
            
            update_data['labels'] = new_labels
        
        # Update the issue with the new state and labels
        return self.update_issue(issue_number, owner=owner, repo=repo, **update_data)
        
    def check_existing_issue(
        self,
        command: 'FailedCommand',
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an issue for the given command already exists.
        
        Args:
            command: The failed command to check
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            **kwargs: Additional query parameters
            
        Returns:
            The existing issue if found, None otherwise
        """
        # Search for issues with a similar title
        issues = self.list_issues(
            owner=owner,
            repo=repo,
            **kwargs
        )
        
        # Look for an issue with a matching title
        search_phrase = f"Fix failed command: {command.title}"
        for issue in issues:
            if search_phrase.lower() in issue.get('title', '').lower():
                return issue
                
        return None
        
    def bulk_create_issues(
        self,
        commands: List['FailedCommand'],
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        dry_run: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Create GitHub issues for multiple failed commands.
        
        Args:
            commands: List of failed commands
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            dry_run: If True, don't actually create issues
            **kwargs: Additional parameters for issue creation
            
        Returns:
            List of created issues or issue data if dry_run
        """
        owner, repo = self._get_owner_repo(owner, repo)
        created_issues = []
        
        for cmd in commands:
            issue_data = {
                'title': f"Fix failed command: {cmd.title}",
                'body': f"""## Failed Command
```
{cmd.command}
```

## Error Output
```
{cmd.error_output}
```

## Source
{cmd.source}""",
                'labels': ['bug', 'automated']
            }
            
            if dry_run:
                created_issues.append(issue_data)
            else:
                try:
                    issue = self.create_issue(
                        owner=owner,
                        repo=repo,
                        issue=issue_data,
                        **kwargs
                    )
                    created_issues.append(issue)
                except Exception as e:
                    print(f"Failed to create issue for command '{cmd.command}': {e}")
                    
        return created_issues
    
    def create_pull_request(
        self,
        title: str,
        head: str,
        base: str = 'main',
        body: str = '',
        draft: bool = False,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            head: The name of the branch where your changes are implemented
            base: The name of the branch you want the changes pulled into
            body: PR description
            draft: Whether to create a draft PR
            owner: Repository owner (optional if set in config)
            repo: Repository name (optional if set in config)
            **kwargs: Additional PR parameters
            
        Returns:
            Created PR data
        """
        owner, repo = self._get_owner_repo(owner, repo)
        endpoint = f'/repos/{owner}/{repo}/pulls'
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body,
            'draft': draft,
            **kwargs
        }
        return self._request('post', endpoint, json=data)
