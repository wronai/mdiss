"""
Konfiguracja pytest dla testów mdiss.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from mdiss.models import FailedCommand, GitHubConfig


@pytest.fixture
def sample_failed_command():
    """Przykładowe nieudane polecenie."""
    return FailedCommand(
        title="Make target: install",
        command="make install",
        source="/home/test/Makefile",
        command_type="make_target",
        status="Failed",
        return_code=2,
        execution_time=1.47,
        output="make[1]: Entering directory",
        error_output="poetry.lock changed significantly",
        metadata={"target": "install", "original_command": "make install"}
    )


@pytest.fixture
def timeout_command():
    """Polecenie z timeout."""
    return FailedCommand(
        title="Long running task",
        command="make run",
        source="/home/test/Makefile",
        command_type="make_target",
        status="Failed",
        return_code=-1,
        execution_time=60.0,
        output="Starting process...",
        error_output="Command timed out after 60 seconds",
        metadata={"target": "run"},
        error_message="Command timed out after 60 seconds"
    )


@pytest.fixture
def npm_command():
    """Polecenie NPM z błędem."""
    return FailedCommand(
        title="NPM script: test",
        command="npm run test",
        source="/home/test/package.json",
        command_type="npm_script",
        status="Failed",
        return_code=254,
        execution_time=2.79,
        output="",
        error_output="npm error code ENOENT\nnpm error syscall open\nnpm error path /home/test/package.json",
        metadata={"script_name": "test", "script_command": "echo test"}
    )


@pytest.fixture
def sample_commands(sample_failed_command, timeout_command, npm_command):
    """Lista przykładowych poleceń."""
    return [sample_failed_command, timeout_command, npm_command]


@pytest.fixture
def github_config():
    """Przykładowa konfiguracja GitHub."""
    return GitHubConfig(
        token="test_token_123",
        owner="test_owner",
        repo="test_repo"
    )


@pytest.fixture
def sample_markdown_content():
    """Przykładowa treść markdown."""
    return """
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
poetry install
```

**Error Output:**
```
poetry.lock changed significantly since poetry.lock was last generated
```

**Metadata:**
- **target:** install
- **original_command:** make install

---

## 2. NPM script: test

**Command:** `npm run test`
**Source:** /home/test/package.json
**Type:** npm_script
**Status:** ❌ Failed
**Return Code:** 254
**Execution Time:** 2.79s

**Output:**
```
```

**Error Output:**
```
npm error code ENOENT
npm error syscall open
npm error path /home/test/package.json
```

**Metadata:**
- **script_name:** test
- **script_command:** echo test

---
"""


@pytest.fixture
def temp_markdown_file(tmp_path, sample_markdown_content):
    """Tymczasowy plik markdown do testów."""
    file_path = tmp_path / "test.md"
    file_path.write_text(sample_markdown_content)
    return file_path


@pytest.fixture
def mock_github_response():
    """Mock odpowiedzi GitHub API."""
    return {
        "id": 123456,
        "number": 1,
        "title": "Fix failed command: Make target: install",
        "body": "## Problem Description\nCommand `make install` is failing...",
        "state": "open",
        "html_url": "https://github.com/test_owner/test_repo/issues/1",
        "labels": [
            {"name": "bug"},
            {"name": "high"},
            {"name": "dependencies"}
        ],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_repo_response():
    """Mock odpowiedzi repozytorium GitHub."""
    return {
        "id": 789012,
        "name": "test_repo",
        "full_name": "test_owner/test_repo",
        "description": "Test repository",
        "private": False,
        "html_url": "https://github.com/test_owner/test_repo"
    }


# Markery pytest
def pytest_configure(config):
    """Konfiguracja pytest."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests"
    )


# Usprawnienie testów - automatyczne użycie mock dla requests w testach jednostkowych
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Automatycznie blokuj prawdziwe requesty HTTP w testach."""

    def mock_request(*args, **kwargs):
        raise RuntimeError(
            "Network access not allowed during testing! "
            "Use responses or mock the request."
        )

    # Tylko dla testów jednostkowych
    if "integration" not in pytest.current_request.keywords:
        monkeypatch.setattr("requests.get", mock_request)
        monkeypatch.setattr("requests.post", mock_request)
        monkeypatch.setattr("requests.put", mock_request)
        monkeypatch.setattr("requests.delete", mock_request)


# Helper do tworzenia mocków
def create_mock_command(
        title="Test Command",
        command="test command",
        command_type="test",
        return_code=1,
        error_output="test error"
):
    """Helper do tworzenia mock command."""
    return FailedCommand(
        title=title,
        command=command,
        source="/test/source",
        command_type=command_type,
        status="Failed",
        return_code=return_code,
        execution_time=1.0,
        output="test output",
        error_output=error_output,
        metadata={"key": "value"}
    )


# Fixture for pytest-current-request
@pytest.fixture
def current_request():
    """Bieżące żądanie pytest."""
    return pytest.current_request if hasattr(pytest, 'current_request') else MagicMock()


# Performance fixtures
@pytest.fixture
def large_command_list():
    """Duża lista poleceń do testów wydajności."""
    commands = []
    for i in range(100):
        commands.append(create_mock_command(
            title=f"Command {i}",
            command=f"test_command_{i}",
            command_type="make_target" if i % 2 == 0 else "npm_script",
            return_code=2 if i % 3 == 0 else 1
        ))
    return commands