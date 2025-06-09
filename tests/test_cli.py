"""
Testy dla CLI.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock

from mdiss.cli import cli


class TestCLI:
    """Testy interfejsu wiersza poleceń."""

    def setup_method(self):
        """Setup przed każdym testem."""
        self.runner = CliRunner()

    def test_cli_version(self):
        """Test wyświetlania wersji."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.60" in result.output

    def test_cli_help(self):
        """Test wyświetlania pomocy."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "mdiss" in result.output
        assert "Markdown Issues" in result.output

    @patch('mdiss.cli.GitHubClient')
    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_dry_run(self, mock_parser, mock_client):
        """Test polecenia create w trybie dry run."""
        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = [
            self._create_mock_command("Test command")
        ]

        # Mock client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        with self.runner.isolated_filesystem():
            # Tworzenie testowego pliku
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo',
                '--token', 'test_token', '--dry-run'
            ])

            assert result.exit_code == 0
            assert "DRY RUN" in result.output
            mock_parser_instance.parse_file.assert_called_once_with("test.md")

    @patch('mdiss.cli.GitHubClient')
    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_with_token_file(self, mock_parser, mock_client):
        """Test polecenia create z plikiem tokenu."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = []

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.test_connection.return_value = True
        mock_client_instance.bulk_create_issues.return_value = []

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")
            Path("token.txt").write_text("test_token_from_file")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo',
                '--token-file', 'token.txt'
            ])

            assert result.exit_code == 0
            # Sprawdź czy GitHubClient został utworzony z tokenem z pliku
            mock_client.assert_called()

    @patch('mdiss.cli.GitHubClient.setup_token')
    @patch('mdiss.cli.GitHubClient')
    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_setup_token(self, mock_parser, mock_client, mock_setup_token):
        """Test polecenia create z automatyczną konfiguracją tokenu."""
        mock_setup_token.return_value = "generated_token"

        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = []

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.test_connection.return_value = True
        mock_client_instance.bulk_create_issues.return_value = []

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo'
            ])

            assert result.exit_code == 0
            mock_setup_token.assert_called_once()

    @patch('mdiss.cli.GitHubClient')
    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_save_token(self, mock_parser, mock_client):
        """Test zapisywania tokenu do pliku."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = []

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.test_connection.return_value = True
        mock_client_instance.bulk_create_issues.return_value = []

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo',
                '--token', 'test_token',
                '--save-token', 'saved_token.txt'
            ])

            assert result.exit_code == 0
            assert Path("saved_token.txt").exists()
            assert Path("saved_token.txt").read_text() == "test_token"

    @patch('mdiss.cli.GitHubClient')
    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_connection_failure(self, mock_parser, mock_client):
        """Test błędu połączenia z GitHub."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.test_connection.return_value = False

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo',
                '--token', 'bad_token'
            ])

            assert result.exit_code == 1
            assert "Błąd połączenia" in result.output

    @patch('mdiss.cli.MarkdownParser')
    def test_create_command_parse_error(self, mock_parser):
        """Test błędu parsowania pliku."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.side_effect = Exception("Parse error")

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'create', 'test.md', 'owner', 'repo',
                '--token', 'test_token', '--dry-run'
            ])

            assert result.exit_code == 1
            assert "Błąd parsowania" in result.output

    def test_create_command_file_not_found(self):
        """Test błędu gdy plik nie istnieje."""
        result = self.runner.invoke(cli, [
            'create', 'nonexistent.md', 'owner', 'repo',
            '--token', 'test_token'
        ])

        assert result.exit_code != 0
        # Click automatycznie sprawdza istnienie pliku

    @patch('mdiss.cli.MarkdownParser')
    def test_analyze_command(self, mock_parser):
        """Test polecenia analyze."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = [
            self._create_mock_command("Test 1"),
            self._create_mock_command("Test 2")
        ]
        mock_parser_instance.get_statistics.return_value = {
            "total_commands": 2,
            "command_types": {"make_target": 2},
            "return_codes": {2: 2},
            "average_execution_time": 1.5,
            "timeout_count": 0,
            "critical_count": 0
        }

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, ['analyze', 'test.md'])

            assert result.exit_code == 0
            assert "Analiza pliku" in result.output
            assert "2" in result.output  # Total commands
            mock_parser_instance.parse_file.assert_called_once_with("test.md")
            mock_parser_instance.get_statistics.assert_called_once()

    @patch('mdiss.cli.MarkdownParser')
    def test_analyze_command_no_commands(self, mock_parser):
        """Test polecenia analyze gdy brak poleceń."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = []

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, ['analyze', 'test.md'])

            assert result.exit_code == 1
            assert "Nie znaleziono żadnych poleceń" in result.output

    @patch('mdiss.cli.GitHubClient')
    def test_list_issues_command(self, mock_client):
        """Test polecenia list-issues."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.list_issues.return_value = [
            {
                "id": 1,
                "number": 1,
                "title": "Test issue",
                "state": "open",
                "labels": [{"name": "bug"}],
                "created_at": "2023-01-01T00:00:00Z"
            }
        ]

        result = self.runner.invoke(cli, [
            'list-issues', 'owner', 'repo',
            '--token', 'test_token'
        ])

        assert result.exit_code == 0
        assert "Issues w repozytorium" in result.output
        assert "Test issue" in result.output
        mock_client_instance.list_issues.assert_called_once_with(state="open", labels="")

    @patch('mdiss.cli.GitHubClient')
    def test_list_issues_with_filters(self, mock_client):
        """Test polecenia list-issues z filtrami."""
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.list_issues.return_value = []

        result = self.runner.invoke(cli, [
            'list-issues', 'owner', 'repo',
            '--token', 'test_token',
            '--state', 'closed',
            '--labels', 'bug,enhancement'
        ])

        assert result.exit_code == 0
        mock_client_instance.list_issues.assert_called_once_with(
            state="closed", labels="bug,enhancement"
        )

    @patch('mdiss.cli.GitHubClient.setup_token')
    def test_setup_command(self, mock_setup_token):
        """Test polecenia setup."""
        mock_setup_token.return_value = "generated_token"

        with self.runner.isolated_filesystem():
            # Symuluj input użytkownika
            result = self.runner.invoke(cli, ['setup'], input='y\n')

            assert result.exit_code == 0
            assert "Konfiguracja mdiss" in result.output
            assert Path(".mdiss_token").exists()
            assert Path(".mdiss_token").read_text() == "generated_token"
            mock_setup_token.assert_called_once()

    @patch('mdiss.cli.MarkdownParser')
    def test_export_command_json(self, mock_parser):
        """Test polecenia export do JSON."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = [
            self._create_mock_command("Test command")
        ]

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'export', 'test.md',
                '--format', 'json',
                '--output', 'output.json'
            ])

            assert result.exit_code == 0
            assert "Eksport zakończony" in result.output
            assert Path("output.json").exists()

            # Sprawdź zawartość JSON
            import json
            data = json.loads(Path("output.json").read_text())
            assert len(data) == 1
            assert data[0]["title"] == "Test command"

    @patch('mdiss.cli.MarkdownParser')
    def test_export_command_csv(self, mock_parser):
        """Test polecenia export do CSV."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = [
            self._create_mock_command("Test command")
        ]

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'export', 'test.md',
                '--format', 'csv',
                '--output', 'output.csv'
            ])

            assert result.exit_code == 0
            assert Path("output.csv").exists()

            # Sprawdź zawartość CSV
            content = Path("output.csv").read_text()
            assert "Title,Command" in content
            assert "Test command" in content

    @patch('mdiss.cli.MarkdownParser')
    def test_export_command_table_to_stdout(self, mock_parser):
        """Test polecenia export tabeli do stdout."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = [
            self._create_mock_command("Test command")
        ]

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'export', 'test.md', '--format', 'table'
            ])

            assert result.exit_code == 0
            assert "Test command" in result.output

    @patch('mdiss.cli.MarkdownParser')
    def test_export_command_no_commands(self, mock_parser):
        """Test polecenia export gdy brak poleceń."""
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_file.return_value = []

        with self.runner.isolated_filesystem():
            Path("test.md").write_text("test content")

            result = self.runner.invoke(cli, [
                'export', 'test.md'
            ])

            assert result.exit_code == 1
            assert "Nie znaleziono żadnych poleceń" in result.output

    def _create_mock_command(self, title="Test Command"):
        """Tworzy mock polecenia do testów."""
        from mdiss.models import FailedCommand
        return FailedCommand(
            title=title,
            command="test command",
            source="/test/source",
            command_type="test_type",
            status="Failed",
            return_code=1,
            execution_time=1.0,
            output="test output",
            error_output="test error",
            metadata={"key": "value"}
        )


class TestCLIHelpers:
    """Testy funkcji pomocniczych CLI."""

    def test_get_token_from_argument(self):
        """Test pobierania tokenu z argumentu."""
        from mdiss.cli import _get_token

        token = _get_token("test_token", None)
        assert token == "test_token"

    def test_get_token_from_file(self):
        """Test pobierania tokenu z pliku."""
        from mdiss.cli import _get_token

        with CliRunner().isolated_filesystem():
            token_file = Path("token.txt")
            token_file.write_text("file_token")

            token = _get_token(None, token_file)
            assert token == "file_token"

    def test_get_token_file_not_exists(self):
        """Test pobierania tokenu z nieistniejącego pliku."""
        from mdiss.cli import _get_token

        token = _get_token(None, Path("nonexistent.txt"))
        assert token is None

    def test_get_token_none(self):
        """Test gdy brak tokenu."""
        from mdiss.cli import _get_token

        token = _get_token(None, None)
        assert token is None


def test_cli_integration():
    """Test integracyjny CLI."""
    runner = CliRunner()

    # Test że CLI się uruchamia
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0

    # Test że wszystkie komendy są dostępne
    commands = ['create', 'analyze', 'list-issues', 'setup', 'export']
    for command in commands:
        assert command in result.output