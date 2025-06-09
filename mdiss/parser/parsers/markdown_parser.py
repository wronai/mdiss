"""Markdown parser implementation."""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

from ..exceptions import ParserError
from ..models import CodeBlock, CommandData, ErrorOutput, Metadata, Section
from .base_parser import BaseParser
from .models import ParserConfig, ParserState


class MarkdownParser(BaseParser):
    """Parser for markdown files with code blocks and command sections."""

    def __init__(self):
        """Initialize the markdown parser."""
        self.config = ParserConfig()
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize regex patterns used by the parser."""
        self.config.patterns = {
            "code_block": re.compile(
                r"```(?:\w+)?\n(.*?)```", re.DOTALL | re.MULTILINE
            ),
            "command": re.compile(r"^\s*\$\s*(.+?)(?:\s*#|$)", re.MULTILINE),
            "section_header": re.compile(
                r"^#{1,3}\s+(.+?)(?:\s*\*\*|:)?\s*$", re.IGNORECASE
            ),
            "metadata": re.compile(r"^\s*[\*\-]?\s*\*\*(.+?):\*\*\s*(.+?)\s*$"),
            "title": re.compile(r"^##\s+\d+\.\s+(.+?)(?:\s*\*\*)?$"),
        }

    def parse(self, content: str, file_path: Optional[str] = None) -> List[CommandData]:
        """Parse markdown content and extract commands.

        Args:
            content: Markdown content to parse
            file_path: Optional path to the source file

        Returns:
            List of CommandData objects
        """
        self.config.content = content
        self.config.file_path = file_path or ""

        # First try the TODO format parser
        todo_commands = self._parse_todo_format()
        if todo_commands:
            return todo_commands

        # Fall back to the default parser
        return self._parse_code_blocks()

    def _parse_todo_format(self) -> List[CommandData]:
        """Parse the TODO.md format with command sections."""
        commands: List[CommandData] = []
        sections = self.config.content.split("---")

        for section in sections:
            command = self._parse_single_section(section)
            if command and command.command:  # Only add if we have a valid command
                commands.append(command)

        return commands

    def _parse_single_section(self, section: str) -> Optional[CommandData]:
        """Parse a single section from TODO format markdown."""
        section = section.strip()
        if not section:
            return None

        # Extract command title from the first line
        lines = section.split("\n")
        title_match = self.config.patterns["title"].match(lines[0].strip())
        if not title_match:
            return None

        title = title_match.group(1).strip()
        command = self._create_command(title)

        # Process the section content
        section_content = "\n".join(lines[1:]).strip()
        if section_content:
            self._process_section_content(section_content, command)

        return command

    def _parse_code_blocks(self) -> List[CommandData]:
        """Parse code blocks from markdown content."""
        commands: List[CommandData] = []

        for match in self.config.patterns["code_block"].finditer(self.config.content):
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
            source=self.config.file_path or "",
            command_type="shell",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=ErrorOutput("", is_from_code_block=False),
            metadata=Metadata(data={"title": title}),
            sections={},
        )

    def _process_section_content(self, content: str, command: CommandData) -> None:
        """Process the content of a section and update the command data."""
        state = ParserState()

        for line in content.split("\n"):
            line = line.rstrip()

            # Handle code blocks
            if line.strip().startswith(("```", "~~~")):
                self._handle_code_block_marker(line, state, command)
                continue

            if state.in_code_block:
                state.code_block_content.append(line)
                continue

            # Handle section headers
            section_match = self.config.patterns["section_header"].match(line)
            if section_match:
                self._finalize_section(command, state)
                state.current_section = self._determine_section_type(
                    section_match.group(1).lower()
                )
                continue

            # Handle regular content
            self._process_regular_line(line, state, command)

        # Finalize the last section
        self._finalize_section(command, state)

    def _handle_code_block_marker(
        self, line: str, state: ParserState, command: CommandData
    ) -> None:
        """Handle code block markers (``` or ~~~) and process code block content."""
        if state.in_code_block:
            # End of code block
            self._finalize_code_block(state, command)
            state.code_block_content = []
            state.in_code_block = False
            state.code_block_language = ""
        else:
            # Start of code block
            state.in_code_block = True
            state.code_block_language = line.strip().strip("`~").strip()

    def _finalize_code_block(self, state: ParserState, command: CommandData) -> None:
        """Finalize and save the current code block."""
        if not state.code_block_content or not state.current_section:
            return

        # Remove the opening ``` line if present
        if state.code_block_content and state.code_block_content[0].startswith(
            ("```", "~~~")
        ):
            state.code_block_content = state.code_block_content[1:]

        block_content = "\n".join(state.code_block_content).strip()
        if not block_content:
            return

        if state.current_section == "error_output":
            command.error_output = ErrorOutput(
                content=block_content, is_from_code_block=True
            )
        else:
            section = command.get_section(state.current_section) or command.add_section(
                state.current_section
            )
            section.code_blocks.append(
                CodeBlock(content=block_content, language=state.code_block_language)
            )

    def _determine_section_type(self, section_name: str) -> Optional[str]:
        """Determine the type of section based on its name."""
        section_mapping = {
            "command": lambda x: "command" in x,
            "output": lambda x: "output" in x and "error" not in x,
            "error_output": lambda x: any(
                term in x for term in ["error", "stderr", "error output"]
            ),
            "suggested_solution": lambda x: "suggested" in x and "solution" in x,
            "metadata": lambda x: "metadata" in x,
        }

        for section_type, condition in section_mapping.items():
            if condition(section_name):
                return section_type
        return None

    def _process_regular_line(
        self, line: str, state: ParserState, command: CommandData
    ) -> None:
        """Process a regular line of content (not a code block or section header)."""
        if not line.strip():
            return

        # Handle key-value pairs
        kv_match = self.config.patterns["metadata"].match(line)
        if kv_match:
            self._update_command_field(
                command, kv_match.group(1).lower().strip(), kv_match.group(2).strip()
            )
        elif state.current_section:
            self._update_section_content(line, state.current_section, command)

    def _update_section_content(
        self, line: str, section_name: str, command: CommandData
    ) -> None:
        """Update the content of a section with the given line."""
        section_handlers = {
            "command": lambda l, cmd: setattr(cmd, "command", l.strip()),
            "output": self._handle_output_section,
            "error_output": self._handle_error_output_section,
            "suggested_solution": lambda l, cmd: cmd.metadata.data.update(
                {"suggested_solution": l}
            ),
            "metadata": lambda l, cmd: self._parse_metadata_line(l, cmd.metadata.data),
        }

        handler = section_handlers.get(section_name)
        if handler:
            handler(line, command)

    def _handle_output_section(self, line: str, command: CommandData) -> None:
        """Handle content for the output section."""
        if command.output:
            command.output += "\n" + line
        else:
            command.output = line

    def _handle_error_output_section(self, line: str, command: CommandData) -> None:
        """Handle content for the error output section."""
        if command.error_output:
            command.error_output.content += "\n" + line
        else:
            command.error_output = ErrorOutput(content=line)

    @staticmethod
    def _parse_metadata_line(line: str, metadata: Dict[str, str]) -> None:
        """Parse a metadata line and update the metadata dictionary."""
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    def _update_command_field(
        self, command: CommandData, field: str, value: str
    ) -> None:
        """Update a command field with the given value."""
        field_handlers = {
            "command": lambda c, v: setattr(c, "command", v.strip("`")),
            "output": lambda c, v: setattr(c, "output", v),
            "error_output": lambda c, v: self._update_error_output(c, v),
            "suggested_solution": lambda c, v: c.metadata.data.update(
                {"suggested_solution": v}
            ),
        }

        handler = field_handlers.get(field)
        if handler:
            handler(command, value)
        else:
            # For other fields, store in metadata
            command.metadata.data[field] = value

    def _update_error_output(self, command: CommandData, value: str) -> None:
        """Update the error output of a command."""
        if command.error_output:
            command.error_output.content += "\n" + value
        else:
            command.error_output = ErrorOutput(content=value)

    def _finalize_section(
        self,
        command: CommandData,
        state: ParserState,
    ) -> None:
        """Finalize the current section by adding any pending code blocks."""
        if state.in_code_block and state.code_block_content:
            self._finalize_code_block(state, command)
            state.code_block_content = []
            state.in_code_block = False
            state.code_block_language = ""

    def parse_failed_commands(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a markdown file containing failed commands and their details.

        The file should contain sections separated by '---' with key-value pairs
        and code blocks for commands and error outputs.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                return []

            # Use the main parser to handle the content
            commands = self.parse(content, str(path))

            # Convert CommandData objects to dictionaries
            return [self._command_to_dict(cmd) for cmd in commands]

        except Exception as e:
            raise ParserError(
                f"Failed to parse failed commands: {str(e)}\n{traceback.format_exc()}"
            ) from e

    def _command_to_dict(self, command: CommandData) -> Dict[str, Any]:
        """Convert a CommandData object to a dictionary."""
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

    def get_statistics(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics from a list of commands."""
        if not commands:
            return self._get_empty_statistics()

        stats = {
            "total_commands": len(commands),
            "error_codes": {},
            "command_types": {},
        }

        # Count failed commands and error codes
        failed_commands = 0
        for cmd in commands:
            # Get exit code, defaulting to 0 if not present
            exit_code = cmd.get("metadata", {}).get("exit_code", 0)
            if exit_code != 0:
                failed_commands += 1

            # Count error codes
            stats["error_codes"][exit_code] = stats["error_codes"].get(exit_code, 0) + 1

            # Count command types
            cmd_type = cmd.get("metadata", {}).get("command_type", "unknown")
            stats["command_types"][cmd_type] = (
                stats["command_types"].get(cmd_type, 0) + 1
            )

        # Calculate success rate
        stats["failed_commands"] = failed_commands
        stats["success_rate"] = (
            1.0 - (failed_commands / stats["total_commands"])
            if stats["total_commands"] > 0
            else 1.0
        )

        return stats
