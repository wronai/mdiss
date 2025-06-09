"""
Markdown Parser for extracting code blocks and commands from markdown files.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import FailedCommand


class MarkdownParser:
    """Parser for extracting code blocks and commands from markdown files.

    This parser supports multiple formats:
    1. Code blocks with shell commands (```bash ... ```)
    2. Markdown sections with command details (## 1. Command: ...)
    """

    def __init__(self):
        """Initialize the MarkdownParser."""
        self.code_block_pattern = re.compile(
            r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL | re.MULTILINE
        )
        self.command_pattern = re.compile(r"^\s*\$\s*(.+?)(?:\s*#|$)", re.MULTILINE)

    def _clean_status(self, status: str) -> str:
        """
        Clean status string by removing emojis and normalizing.

        Args:
            status: Status string to clean

        Returns:
            Cleaned status string
        """
        if not status:
            return ""

        # Remove emojis and extra whitespace
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

    def _parse_metadata(self, metadata_text: str) -> Dict[str, str]:
        """
        Parse metadata from markdown text.

        Args:
            metadata_text: Metadata text in markdown format (list items with **key:** value)

        Returns:
            Dictionary of metadata key-value pairs
        """
        metadata = {}
        if not metadata_text:
            return metadata

        # Match lines with **key:** value format
        pattern = r"\*\*([^:]+):\*\*\s*([^\n]+)"

        for match in re.finditer(pattern, metadata_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key and value:
                metadata[key] = value

        return metadata

    def _update_command_data(
        self, cmd_data: Dict[str, Any], key: str, value: str
    ) -> None:
        """
        Update command data with proper type conversion and key handling.

        Args:
            cmd_data: Dictionary to update with command data
            key: The key to update
            value: The value to set
        """
        if not value:
            return

        key_lower = key.lower()

        if key_lower == "command":
            cmd_data["command"] = value.strip("`")
        elif key_lower == "source":
            cmd_data["source"] = value
        elif key_lower == "type":
            cmd_data["command_type"] = value.lower()
        elif key_lower == "status":
            cmd_data["status"] = self._clean_status(value)
        elif key_lower in ("return code", "return_code"):
            try:
                cmd_data["return_code"] = int(value)
            except (ValueError, TypeError):
                cmd_data["return_code"] = 1
        elif key_lower in ("execution time", "execution_time"):
            try:
                cmd_data["execution_time"] = float(value.rstrip("s").strip())
            except (ValueError, TypeError):
                pass
        elif key_lower in ("output", "stdout"):
            cmd_data["output"] = value
        elif key_lower in ("error", "error_output", "stderr"):
            cmd_data["error_output"] = value
        elif key_lower == "metadata":
            cmd_data["metadata"] = self._parse_metadata(value)

    def _parse_todo_format(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse the TODO.md format with command sections."""
        print(f"[DEBUG] Starting _parse_todo_format for file: {file_path}")
        commands = []
        current_cmd = {}
        current_section = None
        in_code_block = False
        code_block_content = []

        lines = content.split("\n")
        print(f"[DEBUG] Total lines to process: {len(lines)}")

        def finalize_command():
            nonlocal current_cmd, current_section, code_block_content
            if current_cmd:
                print(
                    f"[DEBUG] Finalizing command: {current_cmd.get('title', 'Untitled')}"
                )
                # Save any remaining code block content
                if code_block_content and current_section:
                    content = "\n".join(code_block_content).strip("\n")
                    print(
                        f"[DEBUG] Finalizing section '{current_section}' with content: {content[:100]}..."
                    )
                    if content:
                        if current_section == "error_output":
                            print("[DEBUG] Processing error_output in finalize_command")
                            if "error_output" in current_cmd:
                                current_cmd["error_output"] = (
                                    current_cmd["error_output"].rstrip("\n")
                                    + "\n"
                                    + content
                                )
                                print(f"[DEBUG] Appended to existing error_output")
                            else:
                                current_cmd["error_output"] = content
                                print("[DEBUG] Created new error_output")
                            print(
                                f"[DEBUG] error_output after update: {current_cmd.get('error_output', '')[:100]}..."
                            )
                        else:
                            current_cmd[current_section] = content

                # Clean up the command data
                if "command" in current_cmd:
                    # Remove the backticks from the command if present
                    current_cmd["command"] = current_cmd["command"].strip("`")
                    print(f"[DEBUG] Final command data: {current_cmd}")
                    commands.append(current_cmd)
                else:
                    print("[WARNING] Command missing 'command' field, skipping")
                current_cmd = {}
            else:
                print("[DEBUG] No current command to finalize")
            current_section = None
            code_block_content = []
            print("[DEBUG] Command finalized")

        # Split content into sections using the --- separator
        sections = content.split("---")
        print(f"[DEBUG] Found {len(sections)} sections in the file")

        for section in sections:
            section = section.strip()
            if not section:
                continue

            print(f"[DEBUG] Processing section: {section[:100]}...")

            # Extract the command title from the first line
            lines = section.split("\n")
            title_match = re.match(
                r"^##\s+\d+\.\s+(.+?)(?:\s*\*\*)?$", lines[0].strip()
            )
            if not title_match:
                print(
                    f"[DEBUG] Skipping section with invalid title: {lines[0][:50]}..."
                )
                continue

            title = title_match.group(1).strip()
            print(f"[DEBUG] Found command section: {title}")

            # Initialize new command
            finalize_command()
            current_cmd = {
                "title": title,
                "file": file_path,
                "command": "",
                "command_type": "shell",
                "status": "Failed",
                "return_code": 1,
                "execution_time": 0.0,
                "output": "",
                "error_output": "",
                "source": file_path,
                "metadata": {},
            }

            # Process the section content
            section_content = "\n".join(lines[1:]).strip()
            self._process_section_content(section_content, current_cmd)

        # Finalize the last command
        finalize_command()

        print(f"[DEBUG] Parsed {len(commands)} commands from {file_path}")
        return commands

        return commands

    def _process_section_content(
        self, content: str, current_cmd: Dict[str, Any]
    ) -> None:
        """Process the content of a section and update the command data."""
        lines = content.split("\n")
        current_section = None
        in_code_block = False
        code_block_content = []

        # Debug: Print the raw content being processed
        print(f"\n[DEBUG] ===== PROCESSING SECTION CONTENT =====")
        print(f"[DEBUG] Current command: {current_cmd.get('title', 'Untitled')}")
        print(f"[DEBUG] Initial content (first 200 chars): {content[:200]}...")
        print(f"[DEBUG] Total lines to process: {len(lines)}")
        print("[DEBUG] =======================================")

        for line in lines:
            line = line.rstrip()

            # Handle code blocks
            if line.strip() in ("```", "~~~"):
                print(f"[DEBUG] {'End' if in_code_block else 'Start'} of code block")
                in_code_block = not in_code_block
                if not in_code_block and code_block_content and current_section:
                    # End of code block, save the content
                    block_content = "\n".join(code_block_content).strip("\n")
                    print(
                        f"[DEBUG] Saving code block content for section '{current_section}': {block_content[:100]}..."
                    )
                    if block_content:
                        if current_section == "error_output":
                            print("[DEBUG] Appending to error output section")
                            if "error_output" in current_cmd:
                                current_cmd["error_output"] = (
                                    current_cmd["error_output"].rstrip("\n")
                                    + "\n"
                                    + block_content
                                )
                            else:
                                current_cmd["error_output"] = block_content
                            print(
                                f"[DEBUG] Current error_output: {current_cmd.get('error_output', '')[:100]}..."
                            )
                        else:
                            current_cmd[current_section] = block_content
                    code_block_content = []
                continue

            if in_code_block:
                print(f"[DEBUG] Adding line to code block: {line}")
                code_block_content.append(line)
                continue

            # Check for section headers (supports both **bold** and plain text headers)
            section_match = re.match(r"^###?\s*\*\*(.+?)\*\*:?\s*$", line) or re.match(
                r"^###?\s*([^:]+):?\s*$", line
            )
            if section_match:
                section = section_match.group(1).lower()
                print(f"\n[DEBUG] ===== FOUND SECTION HEADER =====")
                print(f"[DEBUG] Raw line: {line}")
                print(f"[DEBUG] Matched section: {section}")
                print(f"[DEBUG] Group 1: {section_match.group(1)}")
                print(f"[DEBUG] Group 0: {section_match.group(0)}")

                # Finalize previous section if any
                if current_section:
                    print(f"[DEBUG] Finalizing previous section: {current_section}")
                    self._finalize_section(
                        current_cmd, current_section, code_block_content
                    )
                code_block_content = []

                # Determine section type
                if "command" in section:
                    current_section = "command"
                elif "output" in section and "error" not in section:
                    current_section = "output"
                elif any(x in section for x in ["error", "stderr", "error output"]):
                    current_section = "error_output"
                    print("[DEBUG] Set current_section to 'error_output'")
                elif "suggested" in section and "solution" in section:
                    current_section = "suggested_solution"
                elif "metadata" in section:
                    current_section = "metadata"
                else:
                    current_section = None

                print(f"[DEBUG] Section type determined: {current_section}")
                print(f"[DEBUG] Current command state: {current_cmd}")
                print("[DEBUG] =================================")
                continue

            # Skip empty lines outside of sections
            if not line.strip() or not current_section:
                continue

            # Parse key-value pairs for metadata
            if current_section == "metadata":
                kv_match = re.match(r"^\s*[\*\-]?\s*\*\*(.+?):\*\*\s*(.+?)\s*$", line)
                if kv_match:
                    key = kv_match.group(1).strip().lower()
                    value = kv_match.group(2).strip()
                    self._update_command_data(current_cmd, key, value)
            else:
                # For error output sections, always append to preserve all content
                if current_section == "error_output":
                    print(f"\n[DEBUG] ===== PROCESSING ERROR OUTPUT =====")
                    print(f"[DEBUG] Current line: {line}")
                    print(
                        f"[DEBUG] Current error_output before update: {current_cmd.get('error_output', 'NOT SET')}"
                    )

                    # Skip empty lines in error output
                    if line.strip():
                        if "error_output" not in current_cmd:
                            current_cmd["error_output"] = line
                            print("[DEBUG] Created new error_output field")
                        else:
                            # Only add newline if the current error_output is not empty
                            if current_cmd["error_output"]:
                                current_cmd["error_output"] = (
                                    current_cmd["error_output"].rstrip("\n")
                                    + "\n"
                                    + line
                                )
                            else:
                                current_cmd["error_output"] = line
                            print("[DEBUG] Appended to existing error_output")

                        print(
                            f"[DEBUG] error_output after update: {current_cmd.get('error_output', '')[:200]}..."
                        )
                    else:
                        print("[DEBUG] Skipping empty line in error output")
                    print("[DEBUG] ====================================")
                # For other sections, collect the content
                elif current_section not in current_cmd:
                    current_cmd[current_section] = line
                else:
                    current_cmd[current_section] = (
                        current_cmd[current_section].rstrip("\n") + "\n" + line
                    )

    def _finalize_section(
        self,
        current_cmd: Dict[str, Any],
        current_section: str,
        code_block_content: List[str],
    ) -> None:
        """Finalize the current section by saving any pending code block content."""
        if code_block_content and current_section:
            content = "\n".join(code_block_content).strip("\n")
            if content:
                if current_section == "error_output" and "error_output" in current_cmd:
                    current_cmd["error_output"] += "\n" + content
                else:
                    current_cmd[current_section] = content

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a markdown file and extract code blocks and commands.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of dictionaries containing parsed commands and metadata

        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
            # First try the TODO format parser
            todo_commands = self._parse_todo_format(content, file_path)
            if todo_commands:
                return todo_commands

            # Fall back to the default parser
            return self.parse_content(content, file_path=file_path)
        except Exception as e:
            return [
                {
                    "error": f"Failed to parse file {file_path}: {str(e)}",
                    "file": file_path,
                    "commands": [],
                }
            ]

    def parse_content(
        self, content: str, file_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse markdown content and extract code blocks and commands.

        Args:
            content: Markdown content as string
            file_path: Optional path to the source file

        Returns:
            List of dictionaries containing parsed commands and metadata
        """
        results = []

        # Find all code blocks
        for match in self.code_block_pattern.finditer(content):
            code_block = match.group(1).strip()
            if not code_block:
                continue

            # Get line number of the code block
            start_line = content[: match.start()].count("\n") + 1
            end_line = start_line + code_block.count("\n")

            # Extract commands from the code block
            commands = self._extract_commands(code_block)

            results.append(
                {
                    "file": file_path,
                    "code_block": code_block,
                    "start_line": start_line,
                    "end_line": end_line,
                    "commands": commands,
                }
            )

        return results

    def _extract_commands(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract shell commands from text.

        Args:
            text: Text to extract commands from

        Returns:
            List of dictionaries with command information
        """
        commands = []
        for match in self.command_pattern.finditer(text):
            command = match.group(1).strip()
            if command:
                line_number = text[: match.start()].count("\n") + 1
                commands.append(
                    {
                        "command": command,
                        "line_number": line_number,
                        "original_line": match.group(0).strip(),
                    }
                )
        return commands

    def parse_commands(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse and extract commands from markdown content.

        Args:
            content: Markdown content as string

        Returns:
            List of dictionaries with command information
        """
        commands = []
        for block in self.parse_content(content):
            commands.extend(block["commands"])
        return commands

    def find_failed_commands(self, file_path: str) -> List[FailedCommand]:
        """
        Find and return information about failed commands in a markdown file.

        Note: This is a placeholder implementation. In a real scenario, you would
        need to implement actual command execution and failure detection.

        Args:
            file_path: Path to the markdown file

        Returns:
            List of FailedCommand objects
        """
        # This is a simplified implementation
        # In a real scenario, you would execute the commands and check for failures
        return []

    def parse_failed_commands(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse failed commands from a markdown file with specific format.

        Args:
            file_path: Path to the markdown file with failed commands

        Returns:
            List of dictionaries with command information

        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
            sections = content.split("---\n\n## ")

            commands = []
            for section in sections[1:]:  # Skip the first section (header)
                try:
                    # Parse command details from section
                    lines = section.split("\n")
                    title = lines[0].strip("# ").strip()

                    # Initialize command data
                    cmd_data = {
                        "title": title,
                        "command": "",
                        "source": "",
                        "command_type": "make_target",
                        "status": "Failed",
                        "return_code": 1,
                        "execution_time": 0.0,
                        "output": "",
                        "error_output": "",
                        "metadata": {},
                    }

                    # Parse section content
                    current_key = None
                    current_value = []

                    for line in lines[1:]:
                        line = line.strip()
                        if not line:
                            continue

                        # Check for key-value pairs
                        if line.startswith("**"):
                            # Save previous key-value pair
                            if current_key and current_value:
                                value = "\n".join(current_value).strip()
                                if current_key.lower() == "command":
                                    cmd_data["command"] = value.strip("`")
                                elif current_key.lower() == "source":
                                    cmd_data["source"] = value
                                elif current_key.lower() == "type":
                                    cmd_data["command_type"] = value.lower()
                                elif current_key.lower() == "status":
                                    cmd_data["status"] = self._clean_status(value)
                                elif current_key.lower() == "return code":
                                    try:
                                        cmd_data["return_code"] = int(value)
                                    except (ValueError, TypeError):
                                        cmd_data["return_code"] = 1
                                elif current_key.lower() == "execution time":
                                    try:
                                        cmd_data["execution_time"] = float(
                                            value.rstrip("s")
                                        )
                                    except (ValueError, TypeError):
                                        pass

                                current_key = None
                                current_value = []

                            # Start new key-value pair
                            key_match = re.match(r"\*\*([^:]+):\*\*", line)
                            if key_match:
                                current_key = key_match.group(1).strip()
                                value_part = line[key_match.end() :].strip()
                                if value_part:
                                    current_value.append(value_part)
                        elif current_key is not None:
                            current_value.append(line)
                        elif line.startswith("```"):
                            # Skip code block markers
                            continue
                        elif line.startswith("**Metadata:**"):
                            # Parse metadata section
                            metadata_text = "\n".join(lines[lines.index(line) + 1 :])
                            cmd_data["metadata"] = self._parse_metadata(metadata_text)
                            break

                    # Save the last key-value pair
                    if current_key and current_value:
                        value = "\n".join(current_value).strip()
                        if current_key.lower() == "command":
                            cmd_data["command"] = value.strip("`")
                        elif current_key.lower() == "source":
                            cmd_data["source"] = value
                        elif current_key.lower() == "type":
                            cmd_data["command_type"] = value.lower()

                    # Add to commands list
                    commands.append(cmd_data)

                except Exception as e:
                    print(f"Error parsing section: {str(e)}")
                    continue

            return commands

        except Exception as e:
            return [
                {
                    "error": f"Failed to parse failed commands from {file_path}: {str(e)}",
                    "file": file_path,
                    "commands": [],
                }
            ]

    def get_statistics(self, commands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about the commands.

        Args:
            commands: List of command dictionaries

        Returns:
            Dictionary with statistics
        """
        if not commands:
            return {
                "total_commands": 0,
                "failed_commands": 0,
                "success_rate": 1.0,
                "error_codes": {},
                "command_types": {},
            }

        total = len(commands)
        failed = sum(1 for cmd in commands if cmd.get("exit_code", 0) != 0)
        success_rate = (total - failed) / total if total > 0 else 1.0

        error_codes = {}
        command_types = {}

        for cmd in commands:
            # Count error codes
            error_code = cmd.get("exit_code", 0)
            error_codes[error_code] = error_codes.get(error_code, 0) + 1

            # Count command types from metadata if available
            cmd_type = cmd.get("metadata", {}).get("command_type", "unknown")
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1

        return {
            "total_commands": total,
            "failed_commands": failed,
            "success_rate": success_rate,
            "error_codes": error_codes,
            "command_types": command_types,
        }
