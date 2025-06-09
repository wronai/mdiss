"""Base parser interface and common functionality."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import CommandData


class BaseParser(ABC):
    """Base class for all parser implementations."""

    @abstractmethod
    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse content and return a list of commands.

        Args:
            content: The content to parse
            file_path: Optional path to the source file

        Returns:
            List of parsed CommandData objects
        """
        raise NotImplementedError("Subclasses must implement parse")

    @staticmethod
    def _get_empty_statistics() -> Dict[str, Any]:
        """Return an empty statistics dictionary.

        Returns:
            A dictionary with empty/zero statistics
        """
        return {
            "total_commands": 0,
            "failed_commands": 0,
            "success_rate": 1.0,
            "error_codes": {},
            "command_types": {},
        }
