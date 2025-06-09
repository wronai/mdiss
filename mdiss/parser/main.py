"""
Main parser implementation for markdown files.

This module provides the MarkdownParser class which handles parsing of markdown content
to extract commands, code blocks, and metadata in a structured format.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import ParserError
from .models import CommandData, ErrorOutput, Metadata, Section
from .parsers import MarkdownParser as NewMarkdownParser


class MarkdownParser(NewMarkdownParser):
    """
    Parser for extracting code blocks and commands from markdown files.

    This is a compatibility layer that provides the expected interface
    while forwarding to the new implementation.
    """

    def __init__(self):
        """Initialize the markdown parser."""
        super().__init__()
        self.metadata_pattern = re.compile(r"- \*\*(.*?):\*\*\s*(.*)")
        self.file_path: Optional[str] = None
        self.commands: List[CommandData] = []

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse markdown content and extract commands.

        This is a thin wrapper around the new implementation.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects
        """
        self.file_path = file_path or ""
        self.commands = super().parse(content, self.file_path)
        return self.commands

    def parse_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content and return list of command dictionaries.

        This is the main entry point used by tests.

        Args:
            content: Markdown content to parse

        Returns:
            List of command dictionaries
        """
        self.parse(content)
        return [self._command_to_dict(cmd) for cmd in self.commands]

    def _parse_metadata_text(self, text: str) -> Dict[str, str]:
        """Parse metadata text into a dictionary.

        Args:
            text: Metadata text to parse

        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}
        for line in text.strip().split("\n"):
            match = self.metadata_pattern.match(line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                metadata[key] = value
        return metadata

    @staticmethod
    def _clean_status(status: str) -> str:
        """Remove emoji and extra whitespace from status.

        Args:
            status: Status string to clean

        Returns:
            Cleaned status string
        """
        # Remove emoji and extra whitespace
        return re.sub(r"[^\w\s]", "", status).strip()

    def parse_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Parse a markdown file and return list of command dictionaries.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of command dictionaries

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")
        return self.parse_content(content)

    def _clean_status(self, status: str) -> str:
        """Remove emoji and extra whitespace from status.

        Args:
            status: Status string to clean

        Returns:
            Cleaned status string
        """
        # Remove emoji and extra whitespace
        return re.sub(r"[^\w\s]", "", status).strip()

    def _parse_metadata_text(self, text: str) -> Dict[str, str]:
        """Parse metadata text into a dictionary.

        Args:
            text: Metadata text to parse

        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}
        for line in text.strip().split("\n"):
            match = self.metadata_pattern.match(line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                metadata[key] = value
        return metadata

    def _command_to_dict(self, command: CommandData) -> Dict[str, Any]:
        """Convert a CommandData object to a dictionary.

        Args:
            command: CommandData object to convert

        Returns:
            Dictionary representation of the command
        """
        return {
            "command": command.command,
            "output": command.output,
            "error_output": command.error_output.content
            if command.error_output
            else "",
            "metadata": command.metadata.data,
            "sections": [
                {
                    "name": section.name,
                    "content": section.content,
                    "code_blocks": [
                        {"content": cb.content, "language": cb.language}
                        for cb in section.code_blocks
                    ],
                }
                for section in command.sections
            ],
        }

    def parse_failed_commands(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown file containing failed commands and their details.

        The file should contain sections separated by '---' with key-value pairs
        and code blocks for commands and error outputs.

        Args:
            file_path: Path to the markdown file to parse

        Returns:
            List of dictionaries with command information, where each dictionary
            contains the parsed key-value pairs from the markdown file.

        Raises:
            FileNotFoundError: If the file doesn't exist
            ParserError: If there's an error parsing the file
        """
        return super().parse_failed_commands(file_path)

    def get_statistics(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics from a list of commands.

        Args:
            commands: List of command dictionaries to analyze

        Returns:
            Dictionary containing various statistics about the commands
        """
        if not commands:
            return self._get_empty_statistics()

        stats = {
            "total_commands": len(commands),
            "failed_commands": 0,
            "error_codes": {},
            "command_types": {},
        }

        for cmd in commands:
            # Count failed commands
            exit_code = cmd.get("exit_code", 0)
            if exit_code != 0:
                stats["failed_commands"] += 1

            # Count error codes
            stats["error_codes"][str(exit_code)] = (
                stats["error_codes"].get(str(exit_code), 0) + 1
            )

            # Count command types
            cmd_type = cmd.get("metadata", {}).get("command_type", "unknown")
            stats["command_types"][cmd_type] = (
                stats["command_types"].get(cmd_type, 0) + 1
            )

        # Calculate success rate
        stats["success_rate"] = (
            1.0 - (stats["failed_commands"] / stats["total_commands"])
            if stats["total_commands"] > 0
            else 1.0
        )

        return stats

    @staticmethod
    def _get_empty_statistics() -> Dict[str, Any]:
        """Return an empty statistics dictionary.

        Returns:
            Dictionary with empty/zero statistics
        """
        return {
            "total_commands": 0,
            "failed_commands": 0,
            "success_rate": 1.0,
            "error_codes": {},
            "command_types": {},
        }
