"""
Testy dla GitHubClient.
"""

from unittest.mock import MagicMock, patch

import pytest
import responses

from mdiss.github_client import GitHubClient
from mdiss.models import FailedCommand, GitHubConfig, IssueData


class TestGitHubClient:
    """Testy klienta GitHub."""

    def setup_method(self):
        """Setup przed każdym testem."""
        self.config = GitHubConfig(
            token="test_token", owner="test_owner", repo="test_repo"
        )
        self.client = GitHubClient(self.config)

    def test_init_without_config(self):
        """Test inicjalizacji bez konfiguracji."""
        client = GitHubClient()
        assert client.config is None
        assert "Authorization" not in client.session.headers

    def test_init_with_config(self):
        """Test inicjalizacji z konfiguracją."""
        assert self.client.config == self.config
        assert self.client.session.headers["Authorization"] == "token test_token"
        assert self.client.session.headers["Accept"] == "application/vnd.github.v3+json"
        assert self.client.session.headers["User-Agent"] == "mdiss/1.0.60"

    @patch("webbrowser.open")
    @patch("getpass.getpass", return_value="test_token_123")
    def test_setup_token(self, mock_getpass, mock_browser):
        """Test konfiguracji tokenu."""
        token = GitHubClient.setup_token()

        assert token == "test_token_123"
        mock_browser.assert_called_once_with("https://github.com/settings/tokens/new")
        mock_getpass.assert_called_once()

    @patch("getpass.getpass", return_value="")
    def test_setup_token_empty_raises_error(self, mock_getpass):
        """Test że pusty token wywołuje błąd."""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            GitHubClient.setup_token()

    def test_set_config(self):
        """Test ustawiania konfiguracji."""
        new_config = GitHubConfig(token="new_token", owner="new_owner", repo="new_repo")

        client = GitHubClient()
        client.set_config(new_config)

        assert client.config == new_config
        assert client.session.headers["Authorization"] == "token new_token"

    @responses.activate
    def test_test_connection_success(self):
        """Test pomyślnego połączenia."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo",
            json={"name": "test_repo"},
            status=200,
        )

        assert self.client.test_connection() is True

    @responses.activate
    def test_test_connection_failure(self):
        """Test nieudanego połączenia."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo",
            json={"message": "Not Found"},
            status=404,
        )

        assert self.client.test_connection() is False

    def test_test_connection_without_config(self):
        """Test połączenia bez konfiguracji."""
        client = GitHubClient()
        assert client.test_connection() is False

    @responses.activate
    def test_create_issue_success(self):
        """Test pomyślnego tworzenia issue."""
        issue_data = {
            "title": "Test issue",
            "body": "Test body",
            "labels": ["bug", "test"],
        }

        responses.add(
            responses.POST,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json={
                "id": 123,
                "number": 1,
                "title": "Test issue",
                "html_url": "https://github.com/test_owner/test_repo/issues/1",
            },
            status=201,
        )

        result = self.client.create_issue(issue=issue_data)

        assert result["id"] == 123
        assert result["number"] == 1
        assert result["title"] == "Test issue"

    @responses.activate
    def test_create_issue_failure(self):
        """Test nieudanego tworzenia issue."""
        issue_data = IssueData(title="Test issue", body="Test body", labels=["bug"])

        responses.add(
            responses.POST,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json={"message": "Validation Failed"},
            status=422,
        )

        with pytest.raises(Exception):
            self.client.create_issue(issue_data)

    def test_create_issue_without_config(self):
        """Test creating an issue without configuration."""
        client = GitHubClient()
        issue_data = {"title": "Test", "body": "Body", "labels": []}

        with pytest.raises(
            ValueError, match="Owner and repo must be provided or set in config"
        ):
            client.create_issue(issue=issue_data)

    def test_create_issue_from_command(self):
        """Test tworzenia issue z polecenia."""
        command = FailedCommand(
            title="Make target: install",
            command="make install",
            source="/test/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=2,
            execution_time=1.5,
            output="make output",
            error_output="poetry.lock error",
            metadata={"target": "install"},
        )

        with patch.object(self.client, "create_issue") as mock_create:
            mock_create.return_value = {"id": 123}

            result = self.client.create_issue_from_command(command)

            mock_create.assert_called_once()
            call_args = mock_create.call_args[0][0]  # IssueData object

            assert "Fix failed command: Make target: install" == call_args.title
            assert "make install" in call_args.body
            assert "poetry.lock error" in call_args.body
            assert "bug" in call_args.labels
            assert "make_target" in call_args.labels

    def test_create_title(self):
        """Test tworzenia tytułu issue."""
        command = FailedCommand(
            title="Test Command",
            command="test",
            source="/test",
            command_type="test",
            status="Failed",
            return_code=1,
            execution_time=1.0,
            output="",
            error_output="",
            metadata={},
        )

        title = self.client._create_title(command)
        assert title == "Fix failed command: Test Command"

    def test_create_body(self):
        """Test tworzenia treści issue."""
        from mdiss.analyzer import ErrorAnalyzer
        from mdiss.models import AnalysisResult, Category, Priority

        command = FailedCommand(
            title="Test Command",
            command="make test",
            source="/test/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=2,
            execution_time=1.5,
            output="test output",
            error_output="test error",
            metadata={"target": "test"},
        )

        analysis = AnalysisResult(
            priority=Priority.HIGH,
            category=Category.BUILD_FAILURE,
            root_cause="Test root cause",
            suggested_solution="Test solution",
            confidence=0.8,
        )

        body = self.client._create_body(command, analysis)

        assert "make test" in body
        assert "HIGH" in body
        assert "build-failure" in body
        assert "80%" in body
        assert "Test root cause" in body
        assert "Test solution" in body
        assert "test output" in body
        assert "test error" in body
        assert "target" in body
        assert "mdiss" in body  # Footer

    def test_create_labels(self):
        """Test tworzenia labeli."""
        from mdiss.models import AnalysisResult, Category, Priority

        command = FailedCommand(
            title="Test",
            command="test",
            source="/test",
            command_type="make_target",
            status="Failed",
            return_code=-1,
            execution_time=60.0,
            output="",
            error_output="",
            metadata={},
        )

        analysis = AnalysisResult(
            priority=Priority.HIGH,
            category=Category.TIMEOUT,
            root_cause="",
            suggested_solution="",
        )

        labels = self.client._create_labels(command, analysis)

        assert "bug" in labels
        assert "high" in labels
        assert "timeout" in labels
        assert "make_target" in labels
        # Sprawdź że timeout jest dodany dla timeout command
        assert labels.count("timeout") == 1  # Nie powinno być duplikatów

    @responses.activate
    def test_get_repository_info(self):
        """Test pobierania informacji o repozytorium."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo",
            json={
                "name": "test_repo",
                "full_name": "test_owner/test_repo",
                "description": "Test repository",
            },
            status=200,
        )

        info = self.client.get_repository_info()

        assert info["name"] == "test_repo"
        assert info["full_name"] == "test_owner/test_repo"

    @responses.activate
    def test_list_issues(self):
        """Test listowania issues."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json=[
                {"id": 1, "number": 1, "title": "Issue 1", "state": "open"},
                {"id": 2, "number": 2, "title": "Issue 2", "state": "closed"},
            ],
            status=200,
        )

        issues = self.client.list_issues()

        assert len(issues) == 2
        assert issues[0]["title"] == "Issue 1"
        assert issues[1]["title"] == "Issue 2"

    @responses.activate
    def test_list_issues_with_filters(self):
        """Test listowania issues z filtrami."""
        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json=[],
            status=200,
        )

        self.client.list_issues(state="closed", labels="bug,enhancement")

        # Sprawdź czy parametry zostały przekazane
        request = responses.calls[0].request
        assert "state=closed" in request.url
        assert "labels=bug%2Cenhancement" in request.url

    @responses.activate
    def test_check_existing_issue_found(self):
        """Test sprawdzania istniejącego issue - znaleziony."""
        command = FailedCommand(
            title="Test Command",
            command="test",
            source="/test",
            command_type="test",
            status="Failed",
            return_code=1,
            execution_time=1.0,
            output="",
            error_output="",
            metadata={},
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json=[
                {"id": 1, "title": "Fix failed command: Test Command", "state": "open"}
            ],
            status=200,
        )

        existing = self.client.check_existing_issue(command)

        assert existing is not None
        assert existing["id"] == 1
        assert existing["title"] == "Fix failed command: Test Command"

    @responses.activate
    def test_check_existing_issue_not_found(self):
        """Test sprawdzania istniejącego issue - nie znaleziony."""
        command = FailedCommand(
            title="Test Command",
            command="test",
            source="/test",
            command_type="test",
            status="Failed",
            return_code=1,
            execution_time=1.0,
            output="",
            error_output="",
            metadata={},
        )

        responses.add(
            responses.GET,
            "https://api.github.com/repos/test_owner/test_repo/issues",
            json=[{"id": 1, "title": "Different issue title", "state": "open"}],
            status=200,
        )

        existing = self.client.check_existing_issue(command)

        assert existing is None

    def test_bulk_create_issues_dry_run(self):
        """Test bulk tworzenia issues w trybie dry run."""
        commands = [
            FailedCommand(
                title="Test 1",
                command="test1",
                source="/test",
                command_type="test",
                status="Failed",
                return_code=1,
                execution_time=1.0,
                output="",
                error_output="",
                metadata={},
            ),
            FailedCommand(
                title="Test 2",
                command="test2",
                source="/test",
                command_type="test",
                status="Failed",
                return_code=2,
                execution_time=2.0,
                output="",
                error_output="",
                metadata={},
            ),
        ]

        with patch("builtins.print") as mock_print:
            result = self.client.bulk_create_issues(commands, dry_run=True)

            assert result == []  # Dry run nie tworzy issues

            # Sprawdź czy były printy o dry run
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            dry_run_prints = [call for call in print_calls if "DRY RUN" in call]
            assert len(dry_run_prints) == 2  # Po jednym dla każdego polecenia


@pytest.fixture
def sample_failed_command():
    """Przykładowe nieudane polecenie do testów."""
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
        metadata={"target": "install"},
    )


def test_github_config_properties():
    """Test właściwości GitHubConfig."""
    config = GitHubConfig(token="test_token", owner="test_owner", repo="test_repo")

    assert config.repo_url == "test_owner/test_repo"
    assert (
        config.issues_url == "https://api.github.com/repos/test_owner/test_repo/issues"
    )


def test_issue_data_to_dict():
    """Test konwersji IssueData do dict."""
    issue_data = IssueData(
        title="Test Issue",
        body="Test body",
        labels=["bug", "enhancement"],
        assignees=["user1", "user2"],
        milestone=5,
    )

    result = issue_data.to_dict()

    expected = {
        "title": "Test Issue",
        "body": "Test body",
        "labels": ["bug", "enhancement"],
        "assignees": ["user1", "user2"],
        "milestone": 5,
        "state": "open",
    }

    assert result == expected


def test_issue_data_to_dict_minimal():
    """Test konwersji IssueData do dict - minimalne dane."""
    issue_data = IssueData(title="Test Issue", body="Test body", labels=["bug"])

    result = issue_data.to_dict()

    expected = {
        "title": "Test Issue",
        "body": "Test body",
        "labels": ["bug"],
        "assignees": [],
        "state": "open",
    }

    assert result == expected
