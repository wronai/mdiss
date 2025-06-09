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
    
    def __init__(self, token: Optional[str] = None, **kwargs):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token
            **kwargs: Additional arguments like base_url for GitHub Enterprise
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = kwargs.get('base_url', self.BASE_URL)
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Set up the requests session with headers and auth."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'mdiss/1.0.0',
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
        owner: str, 
        repo: str, 
        issue: Union[GitHubIssue, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a new GitHub issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue: GitHubIssue instance or dict with issue data
            
        Returns:
            Created issue data
        """
        if isinstance(issue, GitHubIssue):
            issue_data = issue.to_dict()
        else:
            issue_data = issue
            
        endpoint = f'/repos/{owner}/{repo}/issues'
        return self._request('post', endpoint, json=issue_data)
    
    def create_issue_from_failed_command(
        self,
        owner: str,
        repo: str,
        failed_command: FailedCommand,
        analysis: AnalysisResult,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue from a failed command and its analysis.
        
        Args:
            owner: Repository owner
            repo: Repository name
            failed_command: The failed command
            analysis: Analysis of the failed command
            **kwargs: Additional issue parameters
            
        Returns:
            Created issue data
        """
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
        
        issue = GitHubIssue(
            title=title,
            body=body,
            labels=labels,
            **kwargs
        )
        
        return self.create_issue(owner, repo, issue)
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Get a single issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            
        Returns:
            Issue data
        """
        endpoint = f'/repos/{owner}/{repo}/issues/{issue_number}'
        return self._request('get', endpoint)
    
    def list_issues(
        self, 
        owner: str, 
        repo: str, 
        state: str = 'open', 
        **params
    ) -> List[Dict[str, Any]]:
        """
        List repository issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            **params: Additional query parameters
            
        Returns:
            List of issues
        """
        params['state'] = state
        endpoint = f'/repos/{owner}/{repo}/issues'
        return self._request('get', endpoint, params=params)
    
    def update_issue(
        self, 
        owner: str, 
        repo: str, 
        issue_number: int, 
        **updates
    ) -> Dict[str, Any]:
        """
        Update an existing issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            **updates: Fields to update
            
        Returns:
            Updated issue data
        """
        endpoint = f'/repos/{owner}/{repo}/issues/{issue_number}'
        return self._request('patch', endpoint, json=updates)
    
    def close_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        Close an issue.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
            
        Returns:
            Updated issue data
        """
        return self.update_issue(owner, repo, issue_number, state='closed')
    
    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = 'main',
        body: str = '',
        draft: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            head: The name of the branch where your changes are implemented
            base: The name of the branch you want the changes pulled into
            body: PR description
            draft: Whether to create a draft PR
            **kwargs: Additional PR parameters
            
        Returns:
            Created PR data
        """
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
