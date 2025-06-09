# Markdown Parser Module

A flexible and extensible markdown parser for extracting commands, code blocks, and metadata from markdown files.

## Features

- Supports multiple markdown formats through pluggable handlers
- Extracts commands, output, error output, and metadata
- Handles code blocks with syntax highlighting
- Easy to extend with custom format handlers
- Type hints for better IDE support

## Installation

```bash
pip install -e .
```

## Usage

### Basic Usage

```python
from mdiss.parser import MarkdownParser

# Create a parser instance
parser = MarkdownParser()

# Parse a markdown string
commands = parser.parse("""
## 1. Test command

**Command:** `echo "Hello, World!"`
**Output:**
```
Hello, World!
```
""")

# Access parsed commands
for cmd in commands:
    print(f"Command: {cmd.command}")
    print(f"Output: {cmd.output}")
    if cmd.error_output:
        print(f"Error: {cmd.error_output.content}")
```

### Parsing a File

```python
from mdiss.parser import MarkdownParser

parser = MarkdownParser()
commands = parser.parse_file("TODO.md")
```

### Working with Handlers

```python
from mdiss.parser import MarkdownParser
from mdiss.parser.handlers import TodoFormatHandler, CodeBlockHandler

# Create a parser with specific handlers
parser = MarkdownParser(handlers=[TodoFormatHandler, CodeBlockHandler])

# Or register a new handler
from mdiss.parser.handlers import format_handler_factory
from mdiss.parser.handlers import FormatHandler

class CustomHandler(FormatHandler):
    def can_handle(self, content: str) -> bool:
        return "custom-format" in content

    def parse(self, content: str, file_path: str = None) -> list:
        # Parse the content and return a list of CommandData objects
        pass

# Register the custom handler
format_handler_factory.register_handler(CustomHandler)
```

## Architecture

The parser is built around the concept of format handlers, which are responsible for parsing specific markdown formats. The main components are:

- `MarkdownParser`: The main entry point that coordinates parsing using registered handlers
- `FormatHandler`: Base class for all format handlers
- `CommandData`: Data class representing a parsed command
- `CodeBlock`: Represents a code block in markdown
- `Section`: Represents a section in markdown
- `ErrorOutput`: Represents error output from a command
- `Metadata`: Represents metadata for a command

## Available Handlers

- `TodoFormatHandler`: Parses TODO.md format with numbered sections
- `CodeBlockHandler`: Parses simple markdown code blocks

## Extending the Parser

To add support for a new markdown format, create a new handler class that inherits from `FormatHandler` and implement the required methods:

```python
from mdiss.parser.handlers import FormatHandler
from mdiss.parser.models import CommandData

class MyCustomHandler(FormatHandler):
    def can_handle(self, content: str) -> bool:
        # Return True if this handler can handle the content
        return "my-custom-format" in content

    def parse(self, content: str, file_path: str = None) -> list[CommandData]:
        # Parse the content and return a list of CommandData objects
        commands = []
        # ... parsing logic ...
        return commands
```

Then register the handler:

```python
from mdiss.parser.handlers import format_handler_factory
format_handler_factory.register_handler(MyCustomHandler)
```

## Running Tests

```bash
pytest tests/test_parser.py -v
```

## License

MIT
