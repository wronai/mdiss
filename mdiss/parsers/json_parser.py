"""
JSON log parsers for CI/CD systems.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..models import FailedCommand


class JSONLogParser:
    """Base parser for JSON log files."""

    def __init__(self):
        self.supported_formats = [
            "github-actions",
            "jenkins",
            "gitlab-ci",
            "circleci",
            "generic"
        ]

    def parse_file(self, file_path: str, format_type: str = "auto") -> List[FailedCommand]:
        """
        Parse JSON log file.

        Args:
            file_path: Path to JSON log file
            format_type: Type of format (auto-detect if 'auto')

        Returns:
            List of FailedCommand objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if format_type == "auto":
            format_type = self._detect_format(data)

        return self._parse_by_format(data, format_type, str(path))

    def _detect_format(self, data: Dict) -> str:
        """Auto-detect JSON format type."""
        if isinstance(data, dict):
            if "workflow_run" in data or "action" in data:
                return "github-actions"
            elif "builds" in data or "jenkins" in str(data).lower():
                return "jenkins"
            elif "pipeline" in data or "gitlab" in str(data).lower():
                return "gitlab-ci"
            elif "workflows" in data and "circle" in str(data).lower():
                return "circleci"

        return "generic"

    def _parse_by_format(self, data: Dict, format_type: str, source: str) -> List[FailedCommand]:
        """Parse data by detected format."""
        parsers = {
            "github-actions": GitHubActionsParser(),
            "jenkins": JenkinsParser(),
            "gitlab-ci": GitLabCIParser(),
            "circleci": CircleCIParser(),
            "generic": GenericJSONParser(),
        }

        parser = parsers.get(format_type, GenericJSONParser())
        return parser.parse(data, source)


class GitHubActionsParser:
    """Parser for GitHub Actions logs."""

    def parse(self, data: Dict, source: str) -> List[FailedCommand]:
        """Parse GitHub Actions log data."""
        commands = []

        if "jobs" in data:
            for job_name, job_data in data["jobs"].items():
                commands.extend(self._parse_job(job_name, job_data, source))
        elif "steps" in data:
            # Single job format
            commands.extend(self._parse_job("unknown", data, source))
        else:
            # Try to parse as single step
            if self._is_failed_step(data):
                commands.append(self._create_command_from_step("unknown", data, source))

        return commands

    def _parse_job(self, job_name: str, job_data: Dict, source: str) -> List[FailedCommand]:
        """Parse a single job."""
        commands = []

        if "steps" not in job_data:
            return commands

        for step in job_data["steps"]:
            if self._is_failed_step(step):
                command = self._create_command_from_step(job_name, step, source)
                commands.append(command)

        return commands

    def _is_failed_step(self, step: Dict) -> bool:
        """Check if step failed."""
        conclusion = step.get("conclusion", "").lower()
        return conclusion in ["failure", "error", "cancelled", "timed_out"]

    def _create_command_from_step(self, job_name: str, step: Dict, source: str) -> FailedCommand:
        """Create FailedCommand from step data."""
        step_name = step.get("name", "Unknown Step")
        command = step.get("run", step.get("uses", "unknown command"))

        # Extract error details
        logs = step.get("logs", "")
        error_output = self._extract_error_from_logs(logs)

        # Calculate execution time
        started_at = step.get("started_at")
        completed_at = step.get("completed_at")
        execution_time = self._calculate_duration(started_at, completed_at)

        # Map conclusion to return code
        conclusion = step.get("conclusion", "failure")
        return_code = self._conclusion_to_return_code(conclusion)

        return FailedCommand(
            title=f"GitHub Actions: {job_name} - {step_name}",
            command=command,
            source=source,
            command_type="github_actions",
            status="Failed",
            return_code=return_code,
            execution_time=execution_time,
            output=logs,
            error_output=error_output,
            metadata={
                "job_name": job_name,
                "step_name": step_name,
                "conclusion": conclusion,
                "runner": step.get("runner", "unknown"),
                "workflow_run_id": step.get("workflow_run_id"),
            }
        )

    def _extract_error_from_logs(self, logs: str) -> str:
        """Extract error messages from logs."""
        if not logs:
            return "No error details available"

        error_patterns = [
            r"Error: (.+)",
            r"ERROR: (.+)",
            r"FAILED: (.+)",
            r"Exception: (.+)",
            r"Traceback \(most recent call last\):(.*?)(?=\n\n|\Z)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()

        # Return first few lines if no specific error found
        lines = logs.split('\n')
        error_lines = [line for line in lines if
                       any(keyword in line.lower() for keyword in ['error', 'failed', 'exception'])]

        if error_lines:
            return '\n'.join(error_lines[:5])

        return logs[:500] + "..." if len(logs) > 500 else logs

    def _calculate_duration(self, started_at: Optional[str], completed_at: Optional[str]) -> float:
        """Calculate execution duration."""
        if not started_at or not completed_at:
            return 0.0

        try:
            start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except (ValueError, AttributeError):
            return 0.0

    def _conclusion_to_return_code(self, conclusion: str) -> int:
        """Map GitHub Actions conclusion to return code."""
        mapping = {
            "failure": 1,
            "error": 2,
            "cancelled": 130,  # SIGINT
            "timed_out": -1,
            "skipped": 0,
        }
        return mapping.get(conclusion.lower(), 1)


class JenkinsParser:
    """Parser for Jenkins build logs."""

    def parse(self, data: Dict, source: str) -> List[FailedCommand]:
        """Parse Jenkins log data."""
        commands = []

        if "builds" in data:
            for build_data in data["builds"]:
                commands.extend(self._parse_build(build_data, source))
        else:
            # Single build format
            commands.extend(self._parse_build(data, source))

        return commands

    def _parse_build(self, build_data: Dict, source: str) -> List[FailedCommand]:
        """Parse a single Jenkins build."""
        commands = []

        # Check if build failed
        result = build_data.get("result", "").upper()
        if result not in ["FAILURE", "ABORTED", "UNSTABLE"]:
            return commands

        # Parse build steps
        if "steps" in build_data:
            for step in build_data["steps"]:
                if self._is_failed_step(step):
                    command = self._create_command_from_build_step(build_data, step, source)
                    commands.append(command)
        else:
            # Create command from build itself
            command = self._create_command_from_build(build_data, source)
            commands.append(command)

        return commands

    def _is_failed_step(self, step: Dict) -> bool:
        """Check if Jenkins step failed."""
        return step.get("result", "").upper() in ["FAILURE", "ABORTED", "UNSTABLE"]

    def _create_command_from_build(self, build_data: Dict, source: str) -> FailedCommand:
        """Create FailedCommand from Jenkins build."""
        job_name = build_data.get("jobName", "Unknown Job")
        build_number = build_data.get("number", "unknown")

        console_output = build_data.get("consoleOutput", "")
        error_output = self._extract_jenkins_error(console_output)

        duration = build_data.get("duration", 0) / 1000.0  # Convert from ms to seconds

        result = build_data.get("result", "FAILURE")
        return_code = self._jenkins_result_to_return_code(result)

        return FailedCommand(
            title=f"Jenkins Build: {job_name} #{build_number}",
            command=f"Jenkins build {job_name}",
            source=source,
            command_type="jenkins_build",
            status="Failed",
            return_code=return_code,
            execution_time=duration,
            output=console_output,
            error_output=error_output,
            metadata={
                "job_name": job_name,
                "build_number": build_number,
                "result": result,
                "url": build_data.get("url", ""),
                "node": build_data.get("builtOn", "unknown"),
            }
        )

    def _create_command_from_build_step(self, build_data: Dict, step: Dict, source: str) -> FailedCommand:
        """Create FailedCommand from Jenkins build step."""
        job_name = build_data.get("jobName", "Unknown Job")
        build_number = build_data.get("number", "unknown")
        step_name = step.get("displayName", "Unknown Step")

        return FailedCommand(
            title=f"Jenkins Step: {job_name} #{build_number} - {step_name}",
            command=step.get("script", "unknown command"),
            source=source,
            command_type="jenkins_step",
            status="Failed",
            return_code=self._jenkins_result_to_return_code(step.get("result", "FAILURE")),
            execution_time=step.get("durationInMs", 0) / 1000.0,
            output=step.get("log", ""),
            error_output=self._extract_jenkins_error(step.get("log", "")),
            metadata={
                "job_name": job_name,
                "build_number": build_number,
                "step_name": step_name,
                "result": step.get("result"),
            }
        )

    def _extract_jenkins_error(self, console_output: str) -> str:
        """Extract error from Jenkins console output."""
        if not console_output:
            return "No console output available"

        # Jenkins specific error patterns
        error_patterns = [
            r"Build step '(.+?)' marked build as failure",
            r"ERROR: (.+)",
            r"FATAL: (.+)",
            r"Build failed with exception: (.+)",
            r"Exception in thread \"(.+?)\" (.+)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, console_output, re.MULTILINE)
            if matches:
                return matches[-1] if isinstance(matches[-1], str) else ' '.join(matches[-1])

        # Look for lines with ERROR or FAILED
        lines = console_output.split('\n')
        error_lines = []
        for line in lines:
            if any(keyword in line.upper() for keyword in ['ERROR', 'FAILED', 'EXCEPTION', 'FATAL']):
                error_lines.append(line.strip())

        if error_lines:
            return '\n'.join(error_lines[-5:])  # Last 5 error lines

        # Return last 10 lines as fallback
        return '\n'.join(lines[-10:])

    def _jenkins_result_to_return_code(self, result: str) -> int:
        """Map Jenkins result to return code."""
        mapping = {
            "FAILURE": 1,
            "ABORTED": 130,
            "UNSTABLE": 1,
            "SUCCESS": 0,
        }
        return mapping.get(result.upper(), 1)


class GitLabCIParser:
    """Parser for GitLab CI logs."""

    def parse(self, data: Dict, source: str) -> List[FailedCommand]:
        """Parse GitLab CI log data."""
        commands = []

        if "jobs" in data:
            for job_data in data["jobs"]:
                if self._is_failed_job(job_data):
                    command = self._create_command_from_job(job_data, source)
                    commands.append(command)
        elif "pipeline" in data:
            # Pipeline format
            pipeline = data["pipeline"]
            for job in pipeline.get("jobs", []):
                if self._is_failed_job(job):
                    command = self._create_command_from_job(job, source)
                    commands.append(command)

        return commands

    def _is_failed_job(self, job: Dict) -> bool:
        """Check if GitLab job failed."""
        status = job.get("status", "").lower()
        return status in ["failed", "canceled", "skipped"]

    def _create_command_from_job(self, job: Dict, source: str) -> FailedCommand:
        """Create FailedCommand from GitLab job."""
        job_name = job.get("name", "Unknown Job")
        stage = job.get("stage", "unknown")

        # Extract script commands
        script = job.get("script", [])
        if isinstance(script, list):
            command = " && ".join(script)
        else:
            command = str(script)

        # Extract logs
        logs = job.get("log", job.get("trace", ""))
        error_output = self._extract_gitlab_error(logs)

        duration = job.get("duration", 0)
        status = job.get("status", "failed")

        return FailedCommand(
            title=f"GitLab CI: {stage} - {job_name}",
            command=command,
            source=source,
            command_type="gitlab_ci",
            status="Failed",
            return_code=self._gitlab_status_to_return_code(status),
            execution_time=duration,
            output=logs,
            error_output=error_output,
            metadata={
                "job_name": job_name,
                "stage": stage,
                "status": status,
                "runner": job.get("runner", {}).get("description", "unknown"),
                "pipeline_id": job.get("pipeline", {}).get("id"),
                "job_url": job.get("web_url", ""),
            }
        )

    def _extract_gitlab_error(self, logs: str) -> str:
        """Extract error from GitLab CI logs."""
        if not logs:
            return "No logs available"

        # GitLab CI specific patterns
        error_patterns = [
            r"ERROR: (.+)",
            r"FAILED: (.+)",
            r"Error: (.+)",
            r"Exception: (.+)",
            r"rake aborted!(.+)",
            r"npm ERR! (.+)",
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.MULTILINE)
            if matches:
                return matches[-1].strip()

        # Look for section starting with "Running with gitlab-runner"
        # and find errors after that
        lines = logs.split('\n')
        error_lines = []
        in_execution = False

        for line in lines:
            if "Running with gitlab-runner" in line:
                in_execution = True
            elif in_execution and any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                error_lines.append(line.strip())

        if error_lines:
            return '\n'.join(error_lines[-3:])

        # Return lines containing error keywords
        error_lines = [line for line in lines if
                       any(keyword in line.lower() for keyword in ['error', 'failed', 'exception'])]

        if error_lines:
            return '\n'.join(error_lines[-3:])

        return logs[-500:] if len(logs) > 500 else logs

    def _gitlab_status_to_return_code(self, status: str) -> int:
        """Map GitLab status to return code."""
        mapping = {
            "failed": 1,
            "canceled": 130,
            "skipped": 0,
            "success": 0,
        }
        return mapping.get(status.lower(), 1)


class CircleCIParser:
    """Parser for CircleCI logs."""

    def parse(self, data: Dict, source: str) -> List[FailedCommand]:
        """Parse CircleCI log data."""
        commands = []

        if "workflows" in data:
            for workflow in data["workflows"]:
                commands.extend(self._parse_workflow(workflow, source))
        elif "steps" in data:
            # Single job format
            commands.extend(self._parse_job(data, source))

        return commands

    def _parse_workflow(self, workflow: Dict, source: str) -> List[FailedCommand]:
        """Parse CircleCI workflow."""
        commands = []

        for job in workflow.get("jobs", []):
            if job.get("status") == "failed":
                commands.extend(self._parse_job(job, source))

        return commands

    def _parse_job(self, job: Dict, source: str) -> List[FailedCommand]:
        """Parse CircleCI job."""
        commands = []

        for step in job.get("steps", []):
            if step.get("status") == "failed":
                command = self._create_command_from_step(job, step, source)
                commands.append(command)

        return commands

    def _create_command_from_step(self, job: Dict, step: Dict, source: str) -> FailedCommand:
        """Create FailedCommand from CircleCI step."""
        job_name = job.get("name", "Unknown Job")
        step_name = step.get("name", "Unknown Step")

        return FailedCommand(
            title=f"CircleCI: {job_name} - {step_name}",
            command=step.get("command", "unknown command"),
            source=source,
            command_type="circleci",
            status="Failed",
            return_code=step.get("exit_code", 1),
            execution_time=step.get("run_time_millis", 0) / 1000.0,
            output=step.get("output", ""),
            error_output=step.get("output", ""),
            metadata={
                "job_name": job_name,
                "step_name": step_name,
                "workflow": job.get("workflow_name", "unknown"),
            }
        )


class GenericJSONParser:
    """Generic JSON parser for unknown formats."""

    def parse(self, data: Dict, source: str) -> List[FailedCommand]:
        """Parse generic JSON data."""
        commands = []

        # Try to find common failure indicators
        if self._looks_like_failure(data):
            command = self._create_generic_command(data, source)
            commands.append(command)

        # Recursively search for failures in nested data
        commands.extend(self._search_nested_failures(data, source))

        return commands

    def _looks_like_failure(self, data: Dict) -> bool:
        """Check if data looks like a failure."""
        failure_indicators = [
            "error", "failed", "failure", "exception", "stderr",
            "exit_code", "return_code", "status"
        ]

        data_str = str(data).lower()
        return any(indicator in data_str for indicator in failure_indicators)

    def _search_nested_failures(self, data: Any, source: str, path: str = "") -> List[FailedCommand]:
        """Recursively search for failures in nested data."""
        commands = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key

                if isinstance(value, (dict, list)):
                    commands.extend(self._search_nested_failures(value, source, new_path))
                elif self._is_failure_field(key, value):
                    # Found a potential failure
                    command = self._create_generic_command({key: value}, source, new_path)
                    commands.append(command)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                commands.extend(self._search_nested_failures(item, source, new_path))

        return commands

    def _is_failure_field(self, key: str, value: Any) -> bool:
        """Check if field indicates a failure."""
        key_lower = key.lower()
        failure_keys = ["error", "stderr", "exception", "failed"]

        if any(fkey in key_lower for fkey in failure_keys):
            return True

        if key_lower in ["status", "result", "conclusion"] and str(value).lower() in ["failed", "error", "failure"]:
            return True

        if key_lower in ["exit_code", "return_code"] and isinstance(value, int) and value != 0:
            return True

        return False

    def _create_generic_command(self, data: Dict, source: str, path: str = "") -> FailedCommand:
        """Create generic FailedCommand."""
        title = f"Generic Failure"
        if path:
            title += f" at {path}"

        # Try to extract command info
        command = data.get("command", data.get("cmd", "unknown command"))
        if isinstance(command, list):
            command = " ".join(str(c) for c in command)

        # Extract error information
        error_output = ""
        for key in ["error", "stderr", "exception", "message"]:
            if key in data:
                error_output = str(data[key])
                break

        # Extract return code
        return_code = 1
        for key in ["exit_code", "return_code", "status"]:
            if key in data and isinstance(data[key], int):
                return_code = data[key]
                break

        return FailedCommand(
            title=title,
            command=str(command),
            source=source,
            command_type="generic_json",
            status="Failed",
            return_code=return_code,
            execution_time=data.get("duration", data.get("time", 0)),
            output=str(data.get("stdout", data.get("output", ""))),
            error_output=error_output,
            metadata={"raw_data": data, "path": path}
        )