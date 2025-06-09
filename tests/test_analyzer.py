"""
Testy dla ErrorAnalyzer.
"""

import pytest
from mdiss.analyzer import ErrorAnalyzer
from mdiss.models import FailedCommand, Priority, Category


class TestErrorAnalyzer:
    """Testy analizatora błędów."""

    def setup_method(self):
        """Setup przed każdym testem."""
        self.analyzer = ErrorAnalyzer()

    def test_analyze_poetry_lock_issue(self):
        """Test analizy problemu z poetry.lock."""
        command = FailedCommand(
            title="Make target: install",
            command="make install",
            source="/test/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=2,
            execution_time=1.5,
            output="",
            error_output="pyproject.toml changed significantly since poetry.lock was last generated",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.HIGH
        assert result.category == Category.DEPENDENCIES
        assert "poetry.lock" in result.root_cause.lower()
        assert "poetry lock" in result.suggested_solution

    def test_analyze_timeout_command(self):
        """Test analizy polecenia z timeout."""
        command = FailedCommand(
            title="Test timeout",
            command="make run",
            source="/test/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=-1,
            execution_time=60.0,
            output="",
            error_output="Command timed out after 60 seconds",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.HIGH
        assert result.category == Category.TIMEOUT
        assert "timeout" in result.root_cause.lower()
        assert "timeout" in result.suggested_solution.lower()

    def test_analyze_missing_file(self):
        """Test analizy brakującego pliku."""
        command = FailedCommand(
            title="NPM test",
            command="npm run test",
            source="/test/package.json",
            command_type="npm_script",
            status="Failed",
            return_code=254,
            execution_time=2.0,
            output="",
            error_output="ENOENT: no such file or directory, open '/test/package.json'",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.MEDIUM
        assert result.category == Category.MISSING_FILES
        assert "not found" in result.root_cause.lower() or "enoent" in result.root_cause.lower()

    def test_analyze_permission_error(self):
        """Test analizy błędu uprawnień."""
        command = FailedCommand(
            title="Install package",
            command="pip install --user package",
            source="/test",
            command_type="pip",
            status="Failed",
            return_code=1,
            execution_time=1.0,
            output="",
            error_output="Can not perform a '--user' install. User site-packages are not visible in this virtualenv.",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.MEDIUM
        assert result.category == Category.PERMISSIONS
        assert "virtualenv" in result.root_cause.lower()
        assert "--user" in result.suggested_solution

    def test_analyze_yaml_syntax_error(self):
        """Test analizy błędu składni YAML."""
        command = FailedCommand(
            title="YAML check",
            command="check-yaml",
            source="/test/.pre-commit-config.yaml",
            command_type="yaml",
            status="Failed",
            return_code=1,
            execution_time=0.5,
            output="",
            error_output="could not determine a constructor for the tag 'tag:yaml.org,2002:python/name:materialx.emoji.twemoji'",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.category == Category.SYNTAX
        assert "yaml" in result.root_cause.lower()
        assert "yaml" in result.suggested_solution.lower()

    def test_analyze_critical_error(self):
        """Test analizy krytycznego błędu."""
        command = FailedCommand(
            title="Critical failure",
            command="./app",
            source="/test/app",
            command_type="executable",
            status="Failed",
            return_code=139,
            execution_time=0.1,
            output="",
            error_output="Segmentation fault (core dumped)",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.CRITICAL
        assert "segmentation fault" in result.root_cause.lower()

    def test_analyze_generic_build_failure(self):
        """Test analizy ogólnego błędu budowania."""
        command = FailedCommand(
            title="Build failure",
            command="make build",
            source="/test/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=2,
            execution_time=5.0,
            output="",
            error_output="compilation failed with unknown error",
            metadata={}
        )

        result = self.analyzer.analyze(command)

        assert result.priority == Priority.MEDIUM
        assert result.category == Category.BUILD_FAILURE

    def test_determine_priority_rules(self):
        """Test reguł określania priorytetu."""
        # Timeout command
        timeout_cmd = FailedCommand(
            title="Timeout", command="test", source="/test", command_type="test",
            status="Failed", return_code=-1, execution_time=60.0,
            output="", error_output="timeout", metadata={}
        )
        assert self.analyzer._determine_priority(timeout_cmd) == Priority.HIGH

        # Poetry lock issue
        poetry_cmd = FailedCommand(
            title="Poetry", command="poetry install", source="/test", command_type="poetry",
            status="Failed", return_code=1, execution_time=1.0,
            output="", error_output="poetry.lock file issue", metadata={}
        )
        assert self.analyzer._determine_priority(poetry_cmd) == Priority.HIGH

        # Standard error
        standard_cmd = FailedCommand(
            title="Standard", command="make", source="/test", command_type="make",
            status="Failed", return_code=2, execution_time=1.0,
            output="", error_output="standard error", metadata={}
        )
        assert self.analyzer._determine_priority(standard_cmd) == Priority.MEDIUM

    def test_determine_category_rules(self):
        """Test reguł kategoryzacji."""
        test_cases = [
            ("poetry.lock changed", Category.DEPENDENCIES),
            ("file not found", Category.MISSING_FILES),
            ("permission denied", Category.PERMISSIONS),
            ("command timed out", Category.TIMEOUT),
            ("syntax error in file", Category.SYNTAX),
            ("config file missing", Category.CONFIGURATION),
            ("unknown error", Category.BUILD_FAILURE),
        ]

        for error_text, expected_category in test_cases:
            cmd = FailedCommand(
                title="Test", command="test", source="/test", command_type="test",
                status="Failed", return_code=1, execution_time=1.0,
                output="", error_output=error_text, metadata={}
            )
            assert self.analyzer._determine_category(cmd) == expected_category

    def test_calculate_confidence(self):
        """Test obliczania poziomu pewności."""
        # High confidence - clear pattern
        high_confidence_cmd = FailedCommand(
            title="Poetry", command="poetry install", source="/test", command_type="poetry",
            status="Failed", return_code=1, execution_time=1.0,
            output="", error_output="poetry.lock file needs update", metadata={}
        )
        result = self.analyzer.analyze(high_confidence_cmd)
        assert result.confidence > 0.7

        # Low confidence - unclear pattern
        low_confidence_cmd = FailedCommand(
            title="Unknown", command="unknown_command", source="/test", command_type="unknown",
            status="Failed", return_code=1, execution_time=1.0,
            output="", error_output="some unknown error occurred", metadata={}
        )
        result = self.analyzer.analyze(low_confidence_cmd)
        assert result.confidence <= 0.7

    def test_get_category_statistics(self):
        """Test statystyk kategorii."""
        commands = [
            FailedCommand(
                title="Poetry", command="poetry install", source="/test", command_type="poetry",
                status="Failed", return_code=1, execution_time=1.0,
                output="", error_output="poetry.lock issue", metadata={}
            ),
            FailedCommand(
                title="NPM", command="npm test", source="/test", command_type="npm",
                status="Failed", return_code=1, execution_time=1.0,
                output="", error_output="file not found", metadata={}
            ),
            FailedCommand(
                title="Poetry2", command="poetry update", source="/test", command_type="poetry",
                status="Failed", return_code=1, execution_time=1.0,
                output="", error_output="pyproject.toml changed", metadata={}
            ),
        ]

        stats = self.analyzer.get_category_statistics(commands)

        assert stats[Category.DEPENDENCIES] == 2  # 2 poetry issues
        assert stats[Category.MISSING_FILES] == 1  # 1 file not found

        # Pozostałe kategorie powinny mieć 0
        for category in Category:
            if category not in [Category.DEPENDENCIES, Category.MISSING_FILES]:
                assert stats[category] == 0

    def test_solution_templates_exist(self):
        """Test czy wszystkie kategorie mają szablony rozwiązań."""
        for category in Category:
            assert category in self.analyzer.solution_templates
            template = self.analyzer.solution_templates[category]
            assert isinstance(template, str)
            assert len(template) > 0

    def test_to_labels(self):
        """Test konwersji wyniku analizy do labeli."""
        command = FailedCommand(
            title="Test", command="test", source="/test", command_type="test",
            status="Failed", return_code=1, execution_time=1.0,
            output="", error_output="poetry.lock issue", metadata={}
        )

        result = self.analyzer.analyze(command)
        labels = result.to_labels()

        assert "bug" in labels
        assert result.priority.value in labels
        assert result.category.value in labels
        assert len(labels) == 3