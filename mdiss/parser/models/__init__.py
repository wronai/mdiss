"""
Data models for the markdown parser.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CodeBlock:
    """Represents a code block in markdown."""

    content: str
    language: str = ""
    start_line: int = 0
    end_line: int = 0


@dataclass
class Section:
    """Represents a section in markdown."""

    name: str
    content: str = ""
    code_blocks: List[CodeBlock] = field(default_factory=list)


@dataclass
class ErrorOutput:
    """Represents error output from a command."""

    content: str
    is_from_code_block: bool = False


@dataclass
class Metadata:
    """Represents metadata for a command."""

    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandData:
    """Represents a command extracted from markdown."""

    title: str
    command: str
    source: str
    command_type: str = "shell"
    status: str = "Failed"
    return_code: int = 1
    execution_time: float = 0.0
    output: str = ""
    error_output: Optional[ErrorOutput] = None
    metadata: Metadata = field(default_factory=Metadata)
    sections: Dict[str, Section] = field(default_factory=dict)

    def add_section(self, name: str, content: str = "") -> Section:
        """Add a new section to the command."""
        section = Section(name=name, content=content)
        self.sections[name.lower()] = section
        return section

    def get_section(self, name: str) -> Optional[Section]:
        """Get a section by name (case-insensitive)."""
        return self.sections.get(name.lower())
