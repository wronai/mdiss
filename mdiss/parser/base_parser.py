"""
Base parser class for markdown parsing.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import ParserError
from .models import CommandData


class BaseMarkdownParser(ABC):
    """Abstract base class for markdown parsers."""

    def __init__(self):
        """Initialize the base parser."""
        self.file_path: Optional[str] = None
        self.content: str = ""

    @abstractmethod
    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse markdown content and return a list of commands.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects

        Raises:
            ParserError: If there's an error parsing the content
        """
        pass

    def parse_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse a markdown file and return a list of code blocks with file info.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of dictionaries containing 'code_block' and 'file' keys

        Raises:
            FileNotFoundError: If the file doesn't exist
            ParserError: If there's an error parsing the file
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")

        # Extract code blocks using a simple regex
        import re

        code_blocks = re.findall(r"```(?:\w*\n)?(.*?)```", content, re.DOTALL)

        # Clean up the code blocks
        blocks = []
        for block in code_blocks:
            # Remove leading/trailing whitespace and empty lines
            cleaned = "\n".join(line.rstrip() for line in block.strip().split("\n"))
            if cleaned:  # Only include non-empty blocks
                blocks.append({"code_block": cleaned, "file": str(path.absolute())})

        return blocks

        try:
            content = path.read_text(encoding="utf-8")
            return self.parse(content, str(path.absolute()))
        except Exception as e:
            raise ParserError(f"Failed to parse file {file_path}: {str(e)}") from e

    def _clean_status(self, status: str) -> str:
        """Clean and normalize status string.

        Args:
            status: Status string to clean

        Returns:
            Cleaned status string
        """
        if not status:
            return ""

        # Remove emojis and extra whitespace
        import re

        status = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]",
            "",
            status,
        )
        status = status.strip()

        # Normalize common status values
        status_map = {
            "❌ Failed": "Failed",
            "✅ Passed": "Passed",
            "⚠️ Warning": "Warning",
            "⏱️ Timeout": "Timeout",
        }

        return status_map.get(status, status)
