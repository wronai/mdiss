"""
Handler for parsing markdown code blocks.
"""
import re
from typing import Any, Dict, List, Match, Optional, Pattern

from ..exceptions import InvalidCommandError, ParserError
from ..models import CommandData, ErrorOutput
from . import FormatHandler


class CodeBlockHandler(FormatHandler):
    """Handler for parsing markdown code blocks."""

    def __init__(self):
        """Initialize the code block handler."""
        self.code_block_pattern: Pattern = re.compile(
            r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL | re.MULTILINE
        )

    def can_handle(self, content: str) -> bool:
        """Check if this handler can handle the given content."""
        # This is a fallback handler, so it should always return True
        # but only if no other handlers can handle the content
        return True

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse markdown content and extract commands from code blocks.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects
        """
        commands: List[CommandData] = []

        for match in self.code_block_pattern.finditer(content):
            code_block = match.group(1).strip()
            if not code_block:
                continue

            # Create a command for each code block
            command = CommandData(
                title="Command from code block",
                command=code_block,
                source=file_path or "",
                command_type="shell",
                status="Unknown",
                return_code=0,
                execution_time=0.0,
                output="",
                error_output=None,
                metadata={},
                sections={},
            )

            # Try to detect command type from code block language
            language_match = re.match(r"^```(\w+)", match.group(0))
            if language_match:
                command.command_type = language_match.group(1).lower()

            commands.append(command)

        return commands
