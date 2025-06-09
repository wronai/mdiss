"""
Handler for TODO.md format parsing.
"""
import re
from typing import Any, Dict, List, Match, Optional, Pattern, Tuple

from ..exceptions import InvalidCommandError, ParserError
from ..models import CodeBlock, CommandData, ErrorOutput
from .base_handler import FormatHandler


class TodoFormatHandler(FormatHandler):
    """Handler for parsing TODO.md format markdown files."""

    def can_handle(self, content: str) -> bool:
        """Check if this handler can handle the given content."""
        # Check for the typical TODO.md format with numbered sections
        return bool(re.search(r"^##\s+\d+\.\s+", content, re.MULTILINE))

    """Handler for parsing TODO.md format markdown files."""

    def __init__(self):
        """Initialize the TODO format handler."""
        self.section_header_pattern: Pattern = re.compile(
            r"^###?\s*\*\*(.+?)\*\*:?\s*$|^###?\s*([^:]+):?\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        self.metadata_pattern: Pattern = re.compile(
            r"^\s*[\*\-]?\s*\*\*(.+?):\*\*\s*(.+?)\s*$", re.IGNORECASE
        )
        self.code_block_delimiters = ("```", "~~~")

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse TODO.md format content.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects
        """
        commands: List[CommandData] = []
        sections = self._split_into_sections(content)

        for section in sections:
            if not section.strip():
                continue

            command = self._parse_section(section, file_path)
            if command and command.command:
                commands.append(command)

        return commands

    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into sections separated by horizontal rules (---)."""
        # Handle both Windows and Unix line endings
        return [s.strip() for s in re.split(r"\r?\n-{3,}\r?\n", content)]

    def _parse_section(
        self, section: str, file_path: Optional[str] = None
    ) -> CommandData:
        """Parse a single section into a CommandData object."""
        lines = section.split("\n")
        if not lines:
            raise InvalidCommandError("Empty section")

        # Parse title from the first line
        title_match = re.match(r"^##\s+\d+\.\s+(.+?)(?:\s*\*\*)?$", lines[0].strip())
        if not title_match:
            raise InvalidCommandError(f"Invalid section title: {lines[0]}")

        title = title_match.group(1).strip()
        command = CommandData(
            title=title,
            command="",
            source=file_path or "",
            command_type="shell",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=None,
            metadata={},
            sections={},
        )

        current_section = None
        in_code_block = False
        code_block_content = []

        # Process remaining lines
        for line in lines[1:]:
            line = line.rstrip()

            # Handle code blocks
            if line.strip() in self.code_block_delimiters:
                in_code_block = not in_code_block
                if not in_code_block and code_block_content and current_section:
                    self._process_code_block(
                        "\n".join(code_block_content), current_section, command
                    )
                    code_block_content = []
                continue

            if in_code_block:
                code_block_content.append(line)
                continue

            # Check for section headers
            section_match = self.section_header_pattern.match(line)
            if section_match:
                current_section = self._parse_section_header(section_match)
                continue

            # Skip empty lines outside of sections
            if not line.strip() or not current_section:
                continue

            # Parse content based on current section
            self._process_line(line, current_section, command)

        # Process any remaining code block content
        if in_code_block and code_block_content and current_section:
            self._process_code_block(
                "\n".join(code_block_content), current_section, command
            )

        return command

    def _parse_section_header(self, match: Match) -> Optional[str]:
        """Parse a section header and return the normalized section name."""
        # Try to get the first group (for **bold** headers) or second group (for plain text)
        section_name = match.group(1) or match.group(2)
        if not section_name:
            return None

        section_name = section_name.lower().strip()

        # Map to standard section names
        if "command" in section_name:
            return "command"
        elif "output" in section_name and "error" not in section_name:
            return "output"
        elif any(x in section_name for x in ["error", "stderr"]):
            return "error_output"
        elif "suggested" in section_name and "solution" in section_name:
            return "suggested_solution"
        elif "metadata" in section_name:
            return "metadata"

        return section_name

    def _process_line(self, line: str, section: str, command: CommandData) -> None:
        """Process a line of content based on the current section."""
        if section == "metadata":
            self._parse_metadata_line(line, command)
        elif section == "command":
            command.command = line.strip("`").strip()
        elif section == "output":
            command.output = line
        elif section == "error_output":
            if command.error_output:
                command.error_output.content += "\n" + line
            else:
                command.error_output = ErrorOutput(content=line)
        elif section == "suggested_solution":
            command.metadata["suggested_solution"] = line

    def _parse_metadata_line(self, line: str, command: CommandData) -> None:
        """Parse a metadata line and update the command."""
        match = self.metadata_pattern.match(line)
        if not match:
            return

        key = match.group(1).strip().lower()
        value = match.group(2).strip()

        if key == "command":
            command.command = value.strip("`")
        elif key == "source":
            command.source = value
        elif key == "type":
            command.command_type = value.lower()
        elif key == "status":
            command.status = value
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
            command.metadata[key] = value

    def _process_code_block(
        self, content: str, section: str, command: CommandData
    ) -> None:
        """Process a code block and update the command."""
        if not content.strip():
            return

        if section == "error_output":
            if command.error_output:
                command.error_output.content += "\n" + content
            else:
                command.error_output = ErrorOutput(
                    content=content, is_from_code_block=True
                )
        elif section == "output":
            command.output = content
        elif section == "command":
            command.command = content.strip("`")
        else:
            # For other sections, store as a code block in the section
            if section not in command.sections:
                command.sections[section] = []
            command.sections[section].append(CodeBlock(content=content))
