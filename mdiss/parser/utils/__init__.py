"""
Utility functions for markdown parsing.
"""
import re
from typing import Any, Callable, Dict, List, Match, Optional, Pattern, Tuple


def clean_status(status: str) -> str:
    """Clean and normalize status string.

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


def parse_metadata(metadata_text: str) -> Dict[str, str]:
    """Parse metadata from markdown text.

    Args:
        metadata_text: Metadata text in markdown format

    Returns:
        Dictionary of metadata key-value pairs
    """
    metadata = {}
    if not metadata_text:
        return metadata

    # Match lines with **key:** value format
    pattern = r"\*\*([^:]+):\*\*\s*([^\n]+)"

    for match in re.finditer(pattern, metadata_text):
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        if key and value:
            metadata[key] = value

    return metadata


def extract_sections(content: str, section_pattern: str) -> List[Tuple[str, str]]:
    """Extract sections from markdown content.

    Args:
        content: Markdown content
        section_pattern: Regex pattern to match section headers

    Returns:
        List of (section_header, section_content) tuples
    """
    sections = []
    current_header = None
    current_content = []

    for line in content.split("\n"):
        line = line.rstrip()
        match = re.match(section_pattern, line)

        if match:
            if current_header is not None:
                sections.append((current_header, "\n".join(current_content).strip()))
            current_header = match.group(1).strip()
            current_content = []
        elif current_header is not None:
            current_content.append(line)

    if current_header is not None:
        sections.append((current_header, "\n".join(current_content).strip()))

    return sections


def parse_code_block(block: str) -> Dict[str, Any]:
    """Parse a code block and extract language and content.

    Args:
        block: Code block content including delimiters

    Returns:
        Dictionary with 'language' and 'content' keys
    """
    lines = block.split("\n")
    if not lines:
        return {"language": "", "content": ""}

    first_line = lines[0].strip()
    language = ""
    content_start = 0

    # Check if first line is a code block delimiter
    if first_line.startswith("```"):
        language = first_line[3:].strip()
        content_start = 1

    # Find the end of the code block
    content_end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "```":
            content_end = i
            break

    content = "\n".join(lines[content_start:content_end]).strip()
    return {"language": language, "content": content}


def normalize_section_name(name: str) -> str:
    """Normalize section name to a standard format.

    Args:
        name: Original section name

    Returns:
        Normalized section name
    """
    name = name.lower().strip()

    # Common section name mappings
    section_map = {
        "command": "command",
        "cmd": "command",
        "output": "output",
        "stdout": "output",
        "error": "error_output",
        "stderr": "error_output",
        "error output": "error_output",
        "metadata": "metadata",
        "suggested solution": "suggested_solution",
        "solution": "suggested_solution",
        "suggestion": "suggested_solution",
    }

    return section_map.get(name, name)
