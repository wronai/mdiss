"""Models for the parser module."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ParserState:
    """Class to hold parser state during markdown processing."""

    current_section: Optional[str] = None
    in_code_block: bool = False
    code_block_content: List[str] = field(default_factory=list)
    code_block_language: str = ""


@dataclass
class ParserConfig:
    """Configuration for the parser."""

    file_path: Optional[str] = None
    content: str = ""
    patterns: Dict[str, str] = field(default_factory=dict)
