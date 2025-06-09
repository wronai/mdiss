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
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    UNKNOWN = "unknown"


class FailedCommand(BaseModel):
    """Model representing a failed command."""
    command: str = Field(..., description="The command that failed")
    output: str = Field(..., description="The command output (stderr or stdout)")
    exit_code: int = Field(..., description="The exit code of the command")
    is_timeout: bool = Field(False, description="Whether the command timed out")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata about the command"
    )
    file_path: Optional[str] = Field(
        None, 
        description="Path to the file where the command was found"
    )
    line_number: Optional[int] = Field(
        None, 
        description="Line number where the command was found"
    )


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
