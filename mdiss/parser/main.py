"""
Main parser implementation for markdown files.
"""
import re
from pathlib import Path
from typing import Any, Dict, List, Match, Optional, Pattern

from .base_parser import BaseMarkdownParser
from .exceptions import (
    InvalidCommandError,
    MarkdownSyntaxError,
    ParserError,
    SectionNotFoundError,
)
from .models import CodeBlock, CommandData, ErrorOutput, Metadata, Section


class MarkdownParser(BaseMarkdownParser):
    """
    Parser for extracting code blocks and commands from markdown files.

    This parser supports multiple formats:
    1. Code blocks with shell commands (```bash ... ```)
    2. Markdown sections with command details (## 1. Command: ...)
    """

    def __init__(self):
        """Initialize the markdown parser."""
        super().__init__()
        self.code_block_pattern: Pattern = re.compile(
            r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL | re.MULTILINE
        )
        self.command_pattern: Pattern = re.compile(
            r"^\s*\$\s*(.+?)(?:\s*#|$)", re.MULTILINE
        )
        self.section_header_pattern: Pattern = re.compile(
            r"^#{1,3}\s+(.+?)(?:\s*\*\*|:)?\s*$", re.IGNORECASE
        )
        self.metadata_pattern: Pattern = re.compile(
            r"^\s*[\*\-]?\s*\*\*(.+?):\*\*\s*(.+?)\s*$"
        )

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse markdown content and extract commands.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects
        """
        self.content = content
        self.file_path = file_path or ""

        # First try the TODO format parser
        todo_commands = self._parse_todo_format()
        if todo_commands:
            return todo_commands

        # Fall back to the default parser
        return self._parse_code_blocks()

    def _parse_todo_format(self) -> List[CommandData]:
        """Parse the TODO.md format with command sections."""
        commands: List[CommandData] = []
        sections = self.content.split("---")

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Extract command title from the first line
            lines = section.split("\n")
            title_match = re.match(
                r"^##\s+\d+\.\s+(.+?)(?:\s*\*\*)?$", lines[0].strip()
            )
            if not title_match:
                continue

            title = title_match.group(1).strip()
            command = self._create_command(title)

            # Process the section content
            section_content = "\n".join(lines[1:]).strip()
            self._process_section_content(section_content, command)

            # Validate the command has required fields
            if command.command:  # Only add if we have a command
                commands.append(command)

        return commands

    def _parse_code_blocks(self) -> List[CommandData]:
        """Parse code blocks from markdown content."""
        commands: List[CommandData] = []

        for match in self.code_block_pattern.finditer(self.content):
            code_block = match.group(1).strip()
            if not code_block:
                continue

            # Create a command for each code block
            command = self._create_command("Command from code block")
            command.command = code_block

            # Try to extract command type from code block language
            language = match.group(0).split("\n", 1)[0].strip("`").lower()
            if language and language != "bash":
                command.command_type = language

            commands.append(command)

        return commands

    def _create_command(self, title: str) -> CommandData:
        """Create a new CommandData instance with default values."""
        return CommandData(
            title=title,
            command="",
            source=self.file_path or "",
            command_type="shell",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=None,
            metadata=Metadata(),
            sections={},
        )

    def _process_section_content(self, content: str, command: CommandData) -> None:
        """Process the content of a section and update the command data."""
        lines = content.split("\n")
        current_section = None
        in_code_block = False
        code_block_content = []

        for line in lines:
            line = line.rstrip()

            # Handle code blocks
            if line.strip() in ("```", "~~~"):
                in_code_block = not in_code_block
                if not in_code_block and code_block_content and current_section:
                    # End of code block, save the content
                    block_content = "\n".join(code_block_content).strip("\n")
                    if block_content:
                        code_block = CodeBlock(
                            content=block_content,
                            language="",  # TODO: Detect language if possible
                        )

                        if current_section == "error_output":
                            command.error_output = ErrorOutput(
                                content=block_content, is_from_code_block=True
                            )
                        else:
                            section = command.get_section(
                                current_section
                            ) or command.add_section(current_section)
                            section.code_blocks.append(code_block)

                    code_block_content = []
                continue

            if in_code_block:
                code_block_content.append(line)
                continue

            # Check for section headers
            section_match = self.section_header_pattern.match(line)
            if section_match:
                self._finalize_section(command, current_section, code_block_content)
                code_block_content = []

                section_name = section_match.group(1).lower()

                # Map section name to command field
                if "command" in section_name:
                    current_section = "command"
                elif "output" in section_name and "error" not in section_name:
                    current_section = "output"
                elif any(
                    x in section_name for x in ["error", "stderr", "error output"]
                ):
                    current_section = "error_output"
                elif "suggested" in section_name and "solution" in section_name:
                    current_section = "suggested_solution"
                elif "metadata" in section_name:
                    current_section = "metadata"
                else:
                    current_section = None
                continue

            # Skip empty lines outside of sections
            if not line.strip() or not current_section:
                continue

            # Parse key-value pairs for metadata
            if current_section == "metadata":
                self._parse_metadata(line, command)
            else:
                # For other sections, collect the content
                self._update_command_field(command, current_section, line)

    def _parse_metadata(self, line: str, command: CommandData) -> None:
        """Parse metadata line and update command metadata."""
        match = self.metadata_pattern.match(line)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()

            if key == "command":
                command.command = value.strip("`")
            elif key == "source":
                command.source = value
            elif key == "type":
                command.command_type = value.lower()
            elif key == "status":
                command.status = self._clean_status(value)
            elif key in ("return code", "return_code"):
                try:
                    command.return_code = int(value)
                except (ValueError, TypeError):
                    command.return_code = 1
            elif key in ("execution time", "execution_time"):
                try:
                    command.execution_time = float(value.rstrip("s").strip())
                except (ValueError, TypeError):
                    pass
            elif key in ("output", "stdout"):
                command.output = value
            elif key in ("error", "error_output", "stderr"):
                command.error_output = ErrorOutput(content=value)
            else:
                command.metadata.data[key] = value

    def _update_command_field(
        self, command: CommandData, field: str, value: str
    ) -> None:
        """Update a command field with the given value."""
        if field == "command":
            command.command = value.strip("`")
        elif field == "output":
            command.output = value
        elif field == "error_output":
            if command.error_output:
                command.error_output.content += "\n" + value
            else:
                command.error_output = ErrorOutput(content=value)
        elif field == "suggested_solution":
            # Store suggested solution in metadata
            command.metadata.data["suggested_solution"] = value
        else:
            # For other fields, store in metadata
            command.metadata.data[field] = value

    def _finalize_section(
        self,
        command: CommandData,
        section_name: Optional[str],
        code_block_content: List[str],
    ) -> None:
        """Finalize the current section by saving any pending code block content."""
        if code_block_content and section_name:
            content = "\n".join(code_block_content).strip("\n")
            if content:
                if section_name == "error_output":
                    if command.error_output:
                        command.error_output.content += "\n" + content
                    else:
                        command.error_output = ErrorOutput(content=content)
                else:
                    section = command.get_section(section_name) or command.add_section(
                        section_name
                    )
                    section.content = content
