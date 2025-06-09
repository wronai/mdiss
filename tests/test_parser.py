"""
Testy dla MarkdownParser.
"""

import pytest
from pathlib import Path

from mdiss.parser import MarkdownParser
from mdiss.models import FailedCommand


class TestMarkdownParser:
    """Testy parsera markdown."""

    def setup_method(self):
        """Setup przed każdym testem."""
        self.parser = MarkdownParser()

    def test_parse_empty_content(self):
        """Test parsowania pustej treści."""
        commands = self.parser.parse_content("")
        assert commands == []

    def test_parse_single_command(self):
        """Test parsing a single command."""
        content = """
## 1. Make target: install

**Command:** `make install`
**Source:** /home/tom/github/wronai/domd/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 1.47s

**Output:**
```
make[1]: Entering directory '/home/tom/github/wronai/domd'
poetry install
```

**Error Output:**
```
pyproject.toml changed significantly since poetry.lock was last generated.
```

**Metadata:**
- **target:** install
- **original_command:** make install
---
"""

        commands = self.parser.parse_content(content)

        assert len(commands) == 1
        block = commands[0]
        assert 'code_block' in block
        assert 'commands' in block
        assert 'file' in block
        assert 'start_line' in block
        assert 'end_line' in block

    def test_parse_timeout_command(self):
        """Test parsing a command with timeout."""
        content = """
## 1. Make target: run

**Command:** `make run`
**Source:** /home/test/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** -1
**Execution Time:** 60.00s
**Error:** Command timed out after 60 seconds

**Output:**
```
Starting process...
```

**Error Output:**
```
Process killed due to timeout
```

**Metadata:**
- **target:** run
---
"""

        commands = self.parser.parse_content(content)
        assert len(commands) == 1
        block = commands[0]
        assert 'code_block' in block
        assert 'commands' in block

    def test_parse_multiple_commands(self):
        """Test parsing multiple commands."""
        content = """
## 1. Make target: install

**Command:** `make install`
**Source:** /test/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 1.47s

**Output:**
```
output1
```

**Error Output:**
```
error1
```

**Metadata:**
- **target:** install

---

## 2. NPM script: test

**Command:** `npm run test`
**Source:** /test/package.json
**Type:** npm_script
**Status:** ❌ Failed
**Return Code:** 1
**Execution Time:** 2.3s

**Output:**
```
output2
```

**Error Output:**
```
error2
```

**Metadata:**
- **script_name:** test
---
"""

        commands = self.parser.parse_content(content)
        assert len(commands) == 2
        
        for block in commands:
            assert 'code_block' in block
            assert 'commands' in block
            assert 'file' in block

    def test_parse_invalid_return_code(self):
        """Test parsing with invalid return code."""
        content = """
## 1. Test command

**Command:** `test`
**Source:** /test
**Type:** test
**Status:** Failed
**Return Code:** invalid
**Execution Time:** 1s

**Output:**
```
output
```

**Error Output:**
```
error
```

**Metadata:**
- **key:** value
---
"""

        commands = self.parser.parse_content(content)
        assert len(commands) == 1
        assert 'code_block' in commands[0]

    def test_parse_invalid_execution_time(self):
        """Test parsing with invalid execution time."""
        content = """
## 1. Test command

**Command:** `test`
**Source:** /test
**Type:** test
**Status:** Failed
**Return Code:** 1
**Execution Time:** invalid

**Output:**
```
output
```

**Error Output:**
```
error
```

**Metadata:**
- **key:** value
---
"""
        commands = self.parser.parse_content(content)
        assert len(commands) == 1
        assert 'code_block' in commands[0]

    def test_clean_status(self):
        """Test status cleaning from emojis."""
        assert self.parser._clean_status("❌ Failed") == "Failed"
        assert self.parser._clean_status("✅ Passed") == "Passed"
        assert self.parser._clean_status("Failed") == "Failed"

    def test_parse_metadata(self):
        """Test parsing metadata."""
        metadata_text = """- **target:** install
- **original_command:** make install
- **key with spaces:** value with spaces"""

        metadata = self.parser._parse_metadata(metadata_text)

        assert metadata["target"] == "install"
        assert metadata["original_command"] == "make install"
        assert metadata["key with spaces"] == "value with spaces"

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file("nonexistent.md")

    def test_get_statistics_empty(self):
        """Test statystyk dla pustej listy."""
        stats = self.parser.get_statistics([])
        assert stats == {}

    def test_get_statistics(self):
        """Test generowania statystyk."""
        commands = [
            FailedCommand(
                title="Test 1",
                command="make test",
                source="/test",
                command_type="make_target",
                status="Failed",
                return_code=2,
                execution_time=1.5,
                output="",
                error_output="",
                metadata={}
            ),
            FailedCommand(
                title="Test 2",
                command="npm test",
                source="/test",
                command_type="npm_script",
                status="Failed",
                return_code=1,
                execution_time=2.5,
                output="",
                error_output="",
                metadata={}
            ),
            FailedCommand(
                title="Test 3",
                command="make build",
                source="/test",
                command_type="make_target",
                status="Failed",
                return_code=-1,
                execution_time=60.0,
                output="",
                error_output="",
                metadata={}
            ),
        ]

        stats = self.parser.get_statistics(commands)

        assert stats["total_commands"] == 3
        assert stats["command_types"]["make_target"] == 2
        assert stats["command_types"]["npm_script"] == 1
        assert stats["return_codes"][2] == 1
        assert stats["return_codes"][1] == 1
        assert stats["return_codes"][-1] == 1
        assert stats["average_execution_time"] == 21.33  # (1.5 + 2.5 + 60.0) / 3
        assert stats["timeout_count"] == 1
        assert stats["critical_count"] == 0
        assert stats["most_common_type"] == "make_target"
        assert stats["most_common_return_code"] in [2, 1, -1]  # Wszystkie mają count=1


@pytest.fixture
def sample_markdown_file(tmp_path):
    """Tworzy przykładowy plik markdown do testów."""
    content = """
## 1. Make target: install

**Command:** `make install`
**Source:** /home/test/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 1.47s

**Output:**
```
make[1]: Entering directory
```

**Error Output:**
```
poetry.lock error
```

**Metadata:**
- **target:** install

---
"""

    file_path = tmp_path / "test.md"
    file_path.write_text(content)
    return file_path


def test_parse_file_integration(sample_markdown_file):
    """Test integracyjny parsowania pliku."""
    parser = MarkdownParser()
    commands = parser.parse_file(str(sample_markdown_file))

    assert len(commands) == 1
    assert commands[0].title == "Make target: install"