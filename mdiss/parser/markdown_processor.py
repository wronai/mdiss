"""Markdown processing utilities using Marko library."""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import marko
from marko.block import CodeBlock, Document, Heading
from marko.block import List as MarkoList
from marko.block import ListItem, Paragraph
from marko.inline import Code, Emphasis, Image, Link, RawText, StrongEmphasis


class MarkdownProcessor:
    """Process markdown content using the Marko library."""

    def __init__(
        self,
        content: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ):
        """Initialize the markdown processor.

        Args:
            content: Markdown content as string
            file_path: Path to a markdown file (alternative to content)
        """
        self.content = content
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.content = f.read()

        self.document = marko.parse(self.content) if self.content else None

    def extract_code_blocks(
        self, language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract all code blocks from the markdown.

        Args:
            language: Filter code blocks by language

        Returns:
            List of code blocks with language and content
        """
        if not self.document:
            return []

        code_blocks = []
        for child in self.document.children:
            if isinstance(child, CodeBlock):
                if language is None or child.lang == language:
                    code_blocks.append(
                        {
                            "language": child.lang or "",
                            "content": child.children[0].children,
                        }
                    )
        return code_blocks

    def extract_headings(self, level: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extract headings from the markdown.

        Args:
            level: Filter headings by level (1-6)

        Returns:
            List of headings with level and text
        """
        if not self.document:
            return []

        headings = []
        for child in self.document.children:
            if isinstance(child, Heading):
                if level is None or child.level == level:
                    # Extract text from heading children
                    text = self._extract_text_from_children(child.children)
                    headings.append(
                        {
                            "level": child.level,
                            "text": text,
                            "position": getattr(child, "position", None),
                        }
                    )
        return headings

    def extract_links(self) -> List[Dict[str, str]]:
        """Extract all links from the markdown.

        Returns:
            List of links with text and URL
        """
        if not self.document:
            return []

        links = []
        for child in self.document.children:
            links.extend(self._extract_links_from_element(child))
        return links

    def _extract_links_from_element(self, element) -> List[Dict[str, str]]:
        """Recursively extract links from markdown elements."""
        links = []

        if hasattr(element, "children"):
            for child in getattr(element, "children", []):
                if isinstance(child, Link):
                    links.append(
                        {
                            "text": self._extract_text_from_children([child]),
                            "url": child.dest,
                            "title": getattr(child, "title", ""),
                        }
                    )
                elif hasattr(child, "children"):
                    links.extend(self._extract_links_from_element(child))

        return links

    def _extract_text_from_children(self, children) -> str:
        """Extract text from markdown elements."""
        text_parts = []
        for child in children:
            if hasattr(child, "children"):
                text_parts.append(self._extract_text_from_children(child.children))
            elif hasattr(child, "children") and not child.children:
                continue
            else:
                text = getattr(child, "children", str(child))
                if isinstance(text, list):
                    text = "".join(str(t) for t in text)
                text_parts.append(str(text) if text else "")
        return "".join(text_parts).strip()

    def to_html(self) -> str:
        """Convert markdown to HTML.

        Returns:
            HTML string
        """
        return marko.convert(self.content) if self.content else ""

    def update_code_blocks(
        self, updates: Dict[str, str], language: Optional[str] = None
    ) -> "MarkdownProcessor":
        """Update code blocks in the markdown.

        Args:
            updates: Dictionary mapping old content to new content
            language: Only update code blocks with this language

        Returns:
            New MarkdownProcessor instance with updated content
        """
        if not self.document:
            return self

        # Create a deep copy of the document
        new_document = marko.parse(self.content)

        # Find and update code blocks
        for i, child in enumerate(self.document.children):
            if isinstance(child, CodeBlock) and (
                language is None or child.lang == language
            ):
                content = child.children[0].children
                if content in updates:
                    # Update the code block content
                    new_content = updates[content]
                    new_code_block = CodeBlock(lang=child.lang or "")
                    new_code_block.children = [marko.inline.RawText(new_content)]
                    new_document.children[i] = new_code_block

        # Generate new markdown
        new_markdown = marko.render(new_document)
        return MarkdownProcessor(content=new_markdown)

    def __str__(self) -> str:
        """Return the markdown content as string."""
        return self.content or ""
