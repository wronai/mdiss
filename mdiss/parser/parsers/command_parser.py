"""
Command parsing utilities for markdown files.
"""
import re
from typing import Dict, List, Optional, Tuple


def parse_command_section(section: str, file_path: str) -> Dict[str, any]:
    """Parse a single command section from markdown.

    Args:
        section: The markdown section to parse
        file_path: Path to the source file for reference

    Returns:
        Dictionary containing the parsed command data
    """
    cmd_data = {}
    current_key = None
    in_code_block = False
    code_block_lines = []
    current_code_block_key = None
    metadata = {}

    for line in section.splitlines():
        stripped_line = line.strip()

        # Handle section headers
        if stripped_line.startswith("## "):
            if ":" in stripped_line:
                _, cmd = stripped_line.split(":", 1)
                cmd_data["command"] = cmd.strip()
            continue

        # Handle code blocks
        if stripped_line.startswith("```"):
            if in_code_block and current_code_block_key and code_block_lines:
                code_content = "\n".join(code_block_lines)
                cmd_data[current_code_block_key] = f"```\n{code_content}\n```"
                code_block_lines = []
                current_code_block_key = None
            in_code_block = not in_code_block
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        # Skip empty lines
        if not stripped_line:
            continue

        # Handle key-value pairs
        if "**" in line and ":" in line:
            cmd_data, current_key, metadata = _process_key_value_line(
                line, cmd_data, metadata
            )
            if current_key in ["output", "error_output"]:
                current_code_block_key = current_key
        # Handle metadata section
        elif stripped_line.startswith("**Metadata:**"):
            current_key = "metadata_section"
        # Handle metadata key-value pairs
        elif current_key == "metadata_section" and ":" in line:
            if "**" in line:
                key_part, value_part = line.split(":", 1)
                key = key_part.strip("* ")
                value = value_part.strip()
                metadata[key] = value
        # Continue multi-line values
        elif (
            current_key
            and current_key in cmd_data
            and "**" not in line
            and ":" not in line
        ):
            cmd_data[current_key] += "\n" + line.strip()

    return _finalize_command_data(cmd_data, metadata, file_path)


def _process_key_value_line(
    line: str, cmd_data: Dict[str, any], metadata: Dict[str, str]
) -> Tuple[Dict[str, any], Optional[str], Dict[str, str]]:
    """Process a line containing a key-value pair."""
    parts = line.split("**", 2)
    if len(parts) < 3:
        return cmd_data, None, metadata

    key = parts[1].strip(":")
    value = parts[2].strip(" :\n")

    key_mapping = {
        "Command": "command",
        "Source": "source",
        "Type": "command_type",
        "Status": "status",
        "Return Code": "return_code",
        "Execution Time": "execution_time",
        "Error Output": "error_output",
        "Output": "output",
    }

    current_key = key_mapping.get(key, key.lower().replace(" ", "_"))
    value = value.strip("*` ")

    # Handle special cases
    if current_key == "return_code":
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = 1
    elif current_key == "execution_time":
        try:
            value = float(value.rstrip("s"))
        except (ValueError, TypeError):
            value = 0.0

    cmd_data[current_key] = value
    return cmd_data, current_key, metadata


def _finalize_command_data(
    cmd_data: Dict[str, any], metadata: Dict[str, str], file_path: str
) -> Dict[str, any]:
    """Finalize command data with default values and formatting."""
    if "command" not in cmd_data:
        return {}

    # Format command with backticks if needed
    if not cmd_data["command"].strip().startswith("```"):
        cmd_data["formatted_command"] = f'```bash\n{cmd_data["command"]}\n```'
    else:
        cmd_data["formatted_command"] = cmd_data["command"]

    # Format error output if present
    if "error_output" in cmd_data and not cmd_data["error_output"].strip().startswith(
        "```"
    ):
        cmd_data["formatted_error"] = f'```\n{cmd_data["error_output"]}\n```'

    # Set default values
    defaults = {
        "execution_time": 0.0,
        "status": "Failed",
        "command_type": "shell_command",
        "source": file_path,
        "return_code": 1,
        "metadata": {},
    }

    for key, default in defaults.items():
        if key not in cmd_data:
            cmd_data[key] = default

    # Ensure metadata is a dictionary
    if not isinstance(cmd_data.get("metadata"), dict):
        cmd_data["metadata"] = {}

    # Update with any collected metadata
    cmd_data["metadata"].update(metadata)

    # Add formatted fields to metadata for CLI
    for field in ["formatted_command", "formatted_error"]:
        if field in cmd_data:
            cmd_data["metadata"][field] = cmd_data[field]

    return cmd_data
