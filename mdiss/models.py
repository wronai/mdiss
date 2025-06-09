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
