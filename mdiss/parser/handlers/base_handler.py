"""
Base handler class for markdown format handlers.
"""
from typing import List, Optional

from ..models import CommandData


class FormatHandler:
    """Base class for format handlers."""

    def can_handle(self, content: str) -> bool:
        """Check if this handler can handle the given content."""
        raise NotImplementedError("Subclasses must implement can_handle")

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse the content and return a list of commands."""
        raise NotImplementedError("Subclasses must implement parse")
