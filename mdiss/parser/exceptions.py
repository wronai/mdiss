"""
Exceptions for the markdown parser.
"""


class ParserError(Exception):
    """Base exception for parser errors."""

    pass


class MarkdownSyntaxError(ParserError):
    """Raised when there's a syntax error in the markdown."""

    pass


class SectionNotFoundError(ParserError):
    """Raised when a required section is not found."""

    pass


class InvalidCommandError(ParserError):
    """Raised when a command is invalid or missing required fields."""

    pass
