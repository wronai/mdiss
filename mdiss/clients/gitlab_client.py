"""
GitLab API client for creating issues and merge requests.
"""

import urllib.parse
import webbrowser
from typing import Dict, List, Optional

import requests

from ..analyzer import ErrorAnalyzer
from ..models import AnalysisResult, FailedCommand, IssueData


class GitLabConfig:
    """GitLab configuration."""

    def __init__(
        self, token: str, project_id: str, base_url: str = "https://gitlab.com"
    ):
        self.token = token
        self.project_id = project_id  # Can be "group/project" or numeric ID
        self.base_url = base_url.rstrip("/")

    @property
    def api_url(self) -> str:
        """GitLab API URL."""
        return f"{self.base_url}/api/v4"

    @property
    def project_url(self) -> str:
        """Project API URL."""
        encoded_project = urllib.parse.quote(str(self.project_id), safe="")
        return f"{self.api_url}/projects/{encoded_project}"

    @property
    def issues_url(self) -> str:
        """Issues API URL."""
        return f"{self.project_url}/issues"


class GitLabClient:
    """Client for GitLab API operations."""

    def __init__(self, config: Optional[GitLabConfig] = None):
        self.config = config
        self.analyzer = ErrorAnalyzer()
        self.session = requests.Session()

        if config:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {config.token}",
                    "Content-Type": "application/json",
                    "User-Agent": "mdiss/1.0.60",
                }
            )

    @classmethod
    def setup_token(
        cls,
        gitlab_url: str = "https://gitlab.com",
        description: str = "mdiss - automated issue creation",
    ) -> str:
        """
        Help setup GitLab access token.

        Args:
            gitlab_url: GitLab instance URL
            description: Token description

        Returns:
            Token entered by user
        """
        scopes = ["api", "read_user", "read_repository"]

        url = f"{gitlab_url}/-/profile/personal_access_tokens"

        print("🔑 GitLab Token Setup")
        print("=" * 40)
        print("To use mdiss with GitLab, you need a Personal Access Token with scopes:")
        print("- api (full API access)")
        print("- read_user (read user info)")
        print("- read_repository (read repository)")
        print()
        print(f"Opening GitLab token page: {url}")

        try:
            webbrowser.open(url)
        except Exception:
            print("Cannot open browser. Copy URL manually.")

        print()
        print("Steps:")
        print("1. Set token name (e.g., 'mdiss-token')")
        print("2. Select scopes: api, read_user, read_repository")
        print("3. Set expiration date")
        print("4. Click 'Create personal access token'")
        print("5. Copy the generated token")
        print()

        token = input("Paste GitLab token: ").strip()

        if not token:
            raise ValueError("Token cannot be empty")

        return token

    def set_config(self, config: GitLabConfig) -> None:
        """Set GitLab configuration."""
        self.config = config
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
                "User-Agent": "mdiss/1.0.60",
            }
        )

    def test_connection(self) -> bool:
        """
        Test connection to GitLab API.

        Returns:
            True if connection works
        """
        if not self.config:
            return False

        try:
            response = self.session.get(f"{self.config.project_url}")
            return response.status_code == 200
        except Exception:
            return False

    def get_project_info(self) -> Dict:
        """
        Get project information.

        Returns:
            Project info from GitLab API

        Raises:
            ValueError: When no configuration
            requests.HTTPError: When API error
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        response = self.session.get(self.config.project_url)
        response.raise_for_status()
        return response.json()

    def create_issue_from_command(
        self,
        command: FailedCommand,
        assignee_ids: Optional[List[int]] = None,
        milestone_id: Optional[int] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create GitLab issue from failed command.

        Args:
            command: Failed command to create issue for
            assignee_ids: List of user IDs to assign
            milestone_id: Milestone ID
            labels: Additional labels

        Returns:
            GitLab API response

        Raises:
            ValueError: When no configuration
            requests.HTTPError: When API error
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        # Analyze command
        analysis = self.analyzer.analyze(command)

        # Create issue data
        issue_data = self._create_issue_data(
            command, analysis, assignee_ids, milestone_id, labels
        )

        # Send to GitLab
        return self.create_issue(issue_data)

    def create_issue(self, issue_data: Dict) -> Dict:
        """
        Create issue on GitLab.

        Args:
            issue_data: Issue data dict

        Returns:
            GitLab API response

        Raises:
            ValueError: When no configuration
            requests.HTTPError: When API error
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        response = self.session.post(self.config.issues_url, json=issue_data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def _create_issue_data(
        self,
        command: FailedCommand,
        analysis: AnalysisResult,
        assignee_ids: Optional[List[int]] = None,
        milestone_id: Optional[int] = None,
        additional_labels: Optional[List[str]] = None,
    ) -> Dict:
        """Create issue data for GitLab API."""
        title = self._create_title(command)
        description = self._create_description(command, analysis)
        labels = self._create_labels(command, analysis, additional_labels)

        data = {
            "title": title,
            "description": description,
            "labels": ",".join(labels) if labels else "",
        }

        if assignee_ids:
            data["assignee_ids"] = assignee_ids

        if milestone_id:
            data["milestone_id"] = milestone_id

        return data

    def _create_title(self, command: FailedCommand) -> str:
        """Create issue title."""
        return f"Fix failed command: {command.title}"

    def _create_description(
        self, command: FailedCommand, analysis: AnalysisResult
    ) -> str:
        """Create issue description in GitLab markdown format."""
        description = f"""## Problem Description
Command `{command.command}` is failing consistently.

**Priority**: {analysis.priority.value.upper()}
**Category**: {analysis.category.value}
**Confidence**: {analysis.confidence:.0%}

### Command Details
- **Command**: `{command.command}`
- **Source**: {command.source}
- **Type**: {command.command_type}
- **Return Code**: {command.return_code}
- **Execution Time**: {command.execution_time}s

### Error Analysis
{analysis.root_cause}

### Error Output
```
{command.error_output}
```

### Standard Output
```
{command.output}
```

### Metadata
"""

        for key, value in command.metadata.items():
            description += f"- **{key}**: {value}\n"

        description += f"""
### Expected Behavior
The command should execute successfully without errors.

### Steps to Reproduce
1. Navigate to: `{command.source}`
2. Run: `{command.command}`
3. Observe the error

### Suggested Solution
{analysis.suggested_solution}

---
*Created automatically by [mdiss](https://github.com/wronai/mdiss) v1.0.60*
"""

        return description

    def _create_labels(
        self,
        command: FailedCommand,
        analysis: AnalysisResult,
        additional_labels: Optional[List[str]] = None,
    ) -> List[str]:
        """Create list of labels for GitLab issue."""
        labels = analysis.to_labels()
        labels.append(command.command_type)

        # Additional GitLab-specific labels
        if command.is_timeout:
            labels.append("timeout")

        if command.is_critical:
            labels.append("critical")

        # Add mdiss label
        labels.append("mdiss-generated")

        # Add additional labels
        if additional_labels:
            labels.extend(additional_labels)

        # Remove duplicates and return
        return list(set(labels))

    def list_issues(
        self, state: str = "opened", labels: str = "", per_page: int = 20
    ) -> List[Dict]:
        """
        List issues in project.

        Args:
            state: Issue state (opened/closed/all)
            labels: Labels to filter by (comma-separated)
            per_page: Results per page

        Returns:
            List of issues
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        params = {
            "state": state,
            "per_page": per_page,
            "order_by": "created_at",
            "sort": "desc",
        }

        if labels:
            params["labels"] = labels

        response = self.session.get(self.config.issues_url, params=params)
        response.raise_for_status()
        return response.json()

    def check_existing_issue(self, command: FailedCommand) -> Optional[Dict]:
        """
        Check if issue for command already exists.

        Args:
            command: Command to check for

        Returns:
            Issue if exists, None otherwise
        """
        search_title = f"Fix failed command: {command.title}"

        try:
            issues = self.list_issues(state="all")
            for issue in issues:
                if issue["title"] == search_title:
                    return issue
        except Exception:
            pass  # Ignore errors during check

        return None

    def create_merge_request(
        self,
        source_branch: str,
        target_branch: str = "main",
        title: str = "",
        description: str = "",
    ) -> Dict:
        """
        Create merge request.

        Args:
            source_branch: Source branch name
            target_branch: Target branch name
            title: MR title
            description: MR description

        Returns:
            GitLab API response
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        data = {
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        }

        url = f"{self.config.project_url}/merge_requests"
        response = self.session.post(url, json=data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def bulk_create_issues(
        self,
        commands: List[FailedCommand],
        skip_existing: bool = True,
        dry_run: bool = False,
        assignee_ids: Optional[List[int]] = None,
        milestone_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Create multiple issues at once.

        Args:
            commands: List of failed commands
            skip_existing: Skip if issue already exists
            dry_run: Only simulate creation
            assignee_ids: Default assignees
            milestone_id: Default milestone

        Returns:
            List of created issues
        """
        created_issues = []

        for i, command in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Processing: {command.title}")

            if skip_existing:
                existing = self.check_existing_issue(command)
                if existing:
                    print(f"  ⏭️  Issue already exists: {existing['web_url']}")
                    continue

            if dry_run:
                analysis = self.analyzer.analyze(command)
                print(f"  🧪 DRY RUN - Would create:")
                print(f"      Title: {self._create_title(command)}")
                print(f"      Priority: {analysis.priority.value}")
                print(f"      Category: {analysis.category.value}")
            else:
                try:
                    issue = self.create_issue_from_command(
                        command, assignee_ids=assignee_ids, milestone_id=milestone_id
                    )
                    created_issues.append(issue)
                    print(f"  ✅ Created: {issue['web_url']}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")

        return created_issues

    def get_project_members(self) -> List[Dict]:
        """Get project members for assignment."""
        if not self.config:
            raise ValueError("No GitLab configuration")

        url = f"{self.config.project_url}/members"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_milestones(self) -> List[Dict]:
        """Get project milestones."""
        if not self.config:
            raise ValueError("No GitLab configuration")

        url = f"{self.config.project_url}/milestones"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def create_branch_with_fixes(self, branch_name: str, fixes: List[str]) -> Dict:
        """
        Create branch with automated fixes.

        Args:
            branch_name: Name for new branch
            fixes: List of fix content

        Returns:
            Branch creation response
        """
        if not self.config:
            raise ValueError("No GitLab configuration")

        # This is a simplified version - real implementation would need
        # to analyze the fixes and create appropriate file changes

        data = {"branch": branch_name, "ref": "main"}  # Base branch

        url = f"{self.config.project_url}/repository/branches"
        response = self.session.post(url, json=data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()
