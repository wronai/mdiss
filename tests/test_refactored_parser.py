"""
Tests for the refactored MarkdownParser.
"""
import os
from pathlib import Path

import pytest

from mdiss.parser import MarkdownParser
from mdiss.parser.handlers import CodeBlockHandler, TodoFormatHandler
from mdiss.parser.models import CommandData


class TestRefactoredParser:
    """Tests for the refactored MarkdownParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownParser()

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        commands = self.parser.parse("")
        assert commands == []

    def test_parse_todo_format(self):
        """Test parsing TODO.md format."""
        content = """
## 1. Install dependencies

**Command:** `make install`
**Source:** /test/Makefile
**Type:** make_target
**Status:** Failed
**Return Code:** 2
**Execution Time:** 1.47s

**Output:**
```
Installing dependencies...
```

**Error Output:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Metadata:**
- **target:** install
---
"""
        commands = self.parser.parse(content)
        assert len(commands) == 1

        cmd = commands[0]
        assert cmd.title == "Install dependencies"
        assert cmd.command == "make install"
        assert cmd.source == "/test/Makefile"
        assert cmd.command_type == "make_target"
        assert cmd.status == "Failed"
        assert cmd.return_code == 2
        assert cmd.execution_time == 1.47
        assert "Installing dependencies" in cmd.output
        assert "Could not find a version" in cmd.error_output.content
        assert cmd.metadata.data["target"] == "install"

    def test_parse_code_blocks(self):
        """Test parsing simple code blocks."""
        content = """
# Test Document

```bash
echo "Hello, World!"
```

Some text in between.

```python
print("Python code")
```
"""
        commands = self.parser.parse(content)
        assert len(commands) == 2

        # First command (bash)
        assert commands[0].command == 'echo "Hello, World!"'
        assert commands[0].command_type == "bash"

        # Second command (python)
        assert commands[1].command == 'print("Python code")'
        assert commands[1].command_type == "python"

    def test_parse_file(self, tmp_path):
        """Test parsing a file."""
        content = """
## 1. Test command

**Command:** `test-command`
**Output:**
```
Test output
```
---
"""
        test_file = tmp_path / "test.md"
        test_file.write_text(content)

        commands = self.parser.parse_file(str(test_file))
        assert len(commands) == 1
        assert commands[0].command == "test-command"
        assert commands[0].output.strip() == "Test output"

    def test_error_handling(self):
        """Test error handling during parsing."""
        # This should not raise an exception
        commands = self.parser.parse("Invalid content")
        assert commands == []


class TestTodoFormatHandler:
    """Tests for the TodoFormatHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = TodoFormatHandler()

    def test_can_handle_todo_format(self):
        """Test can_handle method with TODO format."""
        content = """## 1. Test command

**Command:** `test`
"""
        assert self.handler.can_handle(content) is True

    def test_can_handle_non_todo_format(self):
        """Test can_handle with non-TODO format."""
        assert self.handler.can_handle("# Just a heading") is False

    def test_parse_command_section(self):
        """Test parsing a command section."""
        content = """## 1. Test command

**Command:** `echo "test"`
**Output:**
```
Test output
```
**Error Output:**
```
Test error
```
"""
        commands = self.handler.parse(content)
        assert len(commands) == 1
        assert commands[0].command == 'echo "test"'
        assert commands[0].output.strip() == "Test output"
        assert commands[0].error_output.content.strip() == "Test error"


class TestCodeBlockHandler:
    """Tests for the CodeBlockHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = CodeBlockHandler()

    def test_parse_code_blocks(self):
        """Test parsing code blocks."""
        content = """
```bash
echo "Hello"
```

```python
print("World")
```
"""
        commands = self.handler.parse(content)
        assert len(commands) == 2
        assert commands[0].command == 'echo "Hello"'
        assert commands[0].command_type == "bash"
        assert commands[1].command == 'print("World")'
        assert commands[1].command_type == "python"
