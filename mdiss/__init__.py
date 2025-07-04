"""
mdiss - Markdown Issues

Automatyczne generowanie ticketów GitHub na podstawie plików markdown z błędami poleceń.
"""

__version__ = "1.0.60"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"

from .analyzer import ErrorAnalyzer
from .github_client import GitHubClient
from .models import FailedCommand, GitHubConfig, IssueData
from .parser import MarkdownParser

__all__ = [
    "FailedCommand",
    "GitHubConfig",
    "IssueData",
    "MarkdownParser",
    "GitHubClient",
    "ErrorAnalyzer",
]
