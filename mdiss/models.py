"""
Pydantic models for the mdiss package.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for failed commands."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Category(str, Enum):
    """Categories for failed commands."""
    PERMISSION = "permission"
    NETWORK = "network"
    SYNTAX = "syntax"
    DEPENDENCY = "dependency"
    DEPENDENCIES = "dependencies"  # Alias for backward compatibility
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    BUILD_FAILURE = "build_failure"
    UNKNOWN = "unknown"


class FailedCommand(BaseModel):
    """Model representing a failed command."""
    title: str = Field(..., description="Title of the failed command")
    command: str = Field(..., description="The command that failed")
    source: str = Field(..., description="Source file or context of the command")
    command_type: str = Field(..., description="Type of the command")
    status: str = Field(..., description="Status of the command (e.g., 'Failed')")
    return_code: int = Field(..., description="The return code of the command")
    execution_time: float = Field(..., description="Execution time in seconds")
    output: str = Field(default="", description="Standard output of the command")
    error_output: str = Field(default="", description="Error output of the command")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the command"
    )
    
    # Backward compatibility with exit_code alias
    @property
    def exit_code(self) -> int:
        """Alias for return_code for backward compatibility."""
        return self.return_code
        
    @property
    def is_timeout(self) -> bool:
        """Check if the command failed due to a timeout."""
        return self.return_code == -1 and "timeout" in self.status.lower()


class AnalysisResult(BaseModel):
    """Result of analyzing a failed command."""
    priority: Priority = Field(..., description="Priority level of the issue")
    category: Category = Field(..., description="Category of the issue")
    root_cause: Optional[str] = Field(
        None, 
        description="Identified root cause of the failure"
    )
    suggested_solution: Optional[str] = Field(
        None, 
        description="Suggested solution for the issue"
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence level of the analysis (0.0 to 1.0)"
    )
    additional_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional analysis information"
    )


class GitHubConfig(BaseModel):
    """Configuration for GitHub repository access."""
    owner: str = Field(
        ...,
        description="Repository owner (username or organization)"
    )
    repo: str = Field(
        ...,
        description="Repository name"
    )
    token: str = Field(
        ...,
        description="GitHub access token with appropriate permissions"
    )
    base_url: str = Field(
        "https://api.github.com",
        description="Base URL for GitHub API (can be modified for GitHub Enterprise)"
    )
    default_labels: List[str] = Field(
        default_factory=lambda: ["bug", "automated"],
        description="Default labels to apply to created issues"
    )
    dry_run: bool = Field(
        False,
        description="If True, only log actions without making actual API calls"
    )
    
    @property
    def repo_url(self) -> str:
        """Get the repository URL in the format 'owner/repo'."""
        return f"{self.owner}/{self.repo}"
        
    @property
    def issues_url(self) -> str:
        """Get the full GitHub API URL for issues."""
        return f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"


class IssueData(BaseModel):
    """Data model for creating or updating GitHub issues."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the issue"
    )
    body: str = Field(
        ...,
        description="Body content of the issue (supports markdown)"
    )
    labels: List[str] = Field(
        default_factory=list,
        description="List of labels to apply to the issue"
    )
    assignees: List[str] = Field(
        default_factory=list,
        description="List of GitHub usernames to assign to the issue"
    )
    milestone: Optional[int] = Field(
        None,
        description="Milestone ID to associate the issue with"
    )
    state: str = Field(
        "open",
        description="State of the issue (open or closed)",
        pattern="^(open|closed)$"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary for GitHub API compatibility.
        
        Returns:
            Dictionary representation of the issue data
        """
        result = {
            'title': self.title,
            'body': self.body,
            'labels': self.labels,
            'assignees': self.assignees,
            'state': self.state
        }
        
        # Only include milestone if it's set
        if self.milestone is not None:
            result['milestone'] = self.milestone
            
        return result
