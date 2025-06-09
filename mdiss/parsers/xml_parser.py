"""
XML parsers for test reports and build outputs.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from ..models import FailedCommand


class XMLTestParser:
    """Base parser for XML test reports."""

    def __init__(self):
        self.supported_formats = ["junit", "testng", "nunit", "xunit", "generic"]

    def parse_file(
        self, file_path: str, format_type: str = "auto"
    ) -> List[FailedCommand]:
        """
        Parse XML test report file.

        Args:
            file_path: Path to XML file
            format_type: Type of XML format (auto-detect if 'auto')

        Returns:
            List of FailedCommand objects for failed tests
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML file: {e}")

        if format_type == "auto":
            format_type = self._detect_format(root)

        return self._parse_by_format(root, format_type, str(path))

    def _detect_format(self, root: ET.Element) -> str:
        """Auto-detect XML format type."""
        root_tag = root.tag.lower()

        if root_tag == "testsuite" or root_tag == "testsuites":
            return "junit"
        elif root_tag == "testng-results":
            return "testng"
        elif root_tag == "test-run" or "nunit" in root.attrib.get("name", "").lower():
            return "nunit"
        elif (
            root_tag == "assemblies"
            or "xunit" in str(ET.tostring(root, encoding="unicode")).lower()
        ):
            return "xunit"

        return "generic"

    def _parse_by_format(
        self, root: ET.Element, format_type: str, source: str
    ) -> List[FailedCommand]:
        """Parse XML by detected format."""
        parsers = {
            "junit": JUnitParser(),
            "testng": TestNGParser(),
            "nunit": NUnitParser(),
            "xunit": XUnitParser(),
            "generic": GenericXMLParser(),
        }

        parser = parsers.get(format_type, GenericXMLParser())
        return parser.parse(root, source)


class JUnitParser:
    """Parser for JUnit XML reports."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse JUnit XML report."""
        commands = []

        # Handle both single testsuite and testsuites container
        testsuites = []
        if root.tag == "testsuites":
            testsuites = root.findall("testsuite")
        elif root.tag == "testsuite":
            testsuites = [root]

        for testsuite in testsuites:
            commands.extend(self._parse_testsuite(testsuite, source))

        return commands

    def _parse_testsuite(
        self, testsuite: ET.Element, source: str
    ) -> List[FailedCommand]:
        """Parse a single test suite."""
        commands = []
        suite_name = testsuite.get("name", "Unknown Suite")

        # Find all failed test cases
        testcases = testsuite.findall("testcase")
        for testcase in testcases:
            if self._is_failed_testcase(testcase):
                command = self._create_command_from_testcase(
                    testcase, suite_name, source
                )
                commands.append(command)

        return commands

    def _is_failed_testcase(self, testcase: ET.Element) -> bool:
        """Check if test case failed."""
        # Check for failure or error elements
        failure = testcase.find("failure")
        error = testcase.find("error")
        return failure is not None or error is not None

    def _create_command_from_testcase(
        self, testcase: ET.Element, suite_name: str, source: str
    ) -> FailedCommand:
        """Create FailedCommand from failed test case."""
        test_name = testcase.get("name", "Unknown Test")
        class_name = testcase.get("classname", suite_name)

        # Get failure/error details
        failure_elem = testcase.find("failure") or testcase.find("error")
        error_type = failure_elem.tag if failure_elem is not None else "failure"

        error_message = ""
        error_details = ""

        if failure_elem is not None:
            error_message = failure_elem.get("message", "No error message")
            error_details = failure_elem.text or ""

        # Get execution time
        time_str = testcase.get("time", "0")
        try:
            execution_time = float(time_str)
        except ValueError:
            execution_time = 0.0

        return FailedCommand(
            title=f"JUnit Test: {class_name}.{test_name}",
            command=f"Test: {test_name}",
            source=source,
            command_type="junit_test",
            status="Failed",
            return_code=1,
            execution_time=execution_time,
            output="",
            error_output=f"{error_message}\n{error_details}".strip(),
            metadata={
                "test_name": test_name,
                "class_name": class_name,
                "suite_name": suite_name,
                "error_type": error_type,
                "error_message": error_message,
            },
        )


class TestNGParser:
    """Parser for TestNG XML reports."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse TestNG XML report."""
        commands = []

        # Find all test methods
        for suite in root.findall(".//suite"):
            suite_name = suite.get("name", "Unknown Suite")

            for test in suite.findall(".//test"):
                test_name = test.get("name", "Unknown Test")

                for class_elem in test.findall(".//class"):
                    class_name = class_elem.get("name", "Unknown Class")

                    for method in class_elem.findall(".//test-method"):
                        if self._is_failed_method(method):
                            command = self._create_command_from_method(
                                method, class_name, test_name, suite_name, source
                            )
                            commands.append(command)

        return commands

    def _is_failed_method(self, method: ET.Element) -> bool:
        """Check if TestNG method failed."""
        status = method.get("status", "").lower()
        return status == "fail"

    def _create_command_from_method(
        self,
        method: ET.Element,
        class_name: str,
        test_name: str,
        suite_name: str,
        source: str,
    ) -> FailedCommand:
        """Create FailedCommand from failed TestNG method."""
        method_name = method.get("name", "Unknown Method")

        # Get exception details
        exception_elem = method.find(".//exception")
        error_output = ""
        if exception_elem is not None:
            error_class = exception_elem.get("class", "")
            error_message = exception_elem.find("message")
            error_message_text = error_message.text if error_message is not None else ""

            full_stacktrace = exception_elem.find("full-stacktrace")
            stacktrace = full_stacktrace.text if full_stacktrace is not None else ""

            error_output = f"{error_class}: {error_message_text}\n{stacktrace}".strip()

        # Get duration
        duration_ms = method.get("duration-ms", "0")
        try:
            execution_time = float(duration_ms) / 1000.0
        except ValueError:
            execution_time = 0.0

        return FailedCommand(
            title=f"TestNG: {class_name}.{method_name}",
            command=f"Test: {method_name}",
            source=source,
            command_type="testng_test",
            status="Failed",
            return_code=1,
            execution_time=execution_time,
            output="",
            error_output=error_output,
            metadata={
                "method_name": method_name,
                "class_name": class_name,
                "test_name": test_name,
                "suite_name": suite_name,
                "is_config": method.get("is-config", "false") == "true",
            },
        )


class NUnitParser:
    """Parser for NUnit XML reports."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse NUnit XML report."""
        commands = []

        # Find all test cases
        for test_case in root.findall(".//test-case"):
            if self._is_failed_testcase(test_case):
                command = self._create_command_from_testcase(test_case, source)
                commands.append(command)

        return commands

    def _is_failed_testcase(self, test_case: ET.Element) -> bool:
        """Check if NUnit test case failed."""
        result = test_case.get("result", "").lower()
        return result in ["failed", "error"]

    def _create_command_from_testcase(
        self, test_case: ET.Element, source: str
    ) -> FailedCommand:
        """Create FailedCommand from failed NUnit test case."""
        test_name = test_case.get("name", "Unknown Test")
        full_name = test_case.get("fullname", test_name)

        # Get failure details
        failure_elem = test_case.find("failure")
        error_output = ""
        if failure_elem is not None:
            message_elem = failure_elem.find("message")
            stack_trace_elem = failure_elem.find("stack-trace")

            message = message_elem.text if message_elem is not None else ""
            stack_trace = stack_trace_elem.text if stack_trace_elem is not None else ""

            error_output = f"{message}\n{stack_trace}".strip()

        # Get duration
        duration = test_case.get("duration", "0")
        try:
            execution_time = float(duration)
        except ValueError:
            execution_time = 0.0

        return FailedCommand(
            title=f"NUnit Test: {test_name}",
            command=f"Test: {test_name}",
            source=source,
            command_type="nunit_test",
            status="Failed",
            return_code=1,
            execution_time=execution_time,
            output="",
            error_output=error_output,
            metadata={
                "test_name": test_name,
                "full_name": full_name,
                "result": test_case.get("result", ""),
                "assertions": test_case.get("asserts", "0"),
            },
        )


class XUnitParser:
    """Parser for xUnit XML reports."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse xUnit XML report."""
        commands = []

        # Find all test collections/assemblies
        for assembly in root.findall(".//assembly"):
            for collection in assembly.findall(".//collection"):
                for test in collection.findall(".//test"):
                    if self._is_failed_test(test):
                        command = self._create_command_from_test(test, source)
                        commands.append(command)

        return commands

    def _is_failed_test(self, test: ET.Element) -> bool:
        """Check if xUnit test failed."""
        result = test.get("result", "").lower()
        return result == "fail"

    def _create_command_from_test(self, test: ET.Element, source: str) -> FailedCommand:
        """Create FailedCommand from failed xUnit test."""
        test_name = test.get("name", "Unknown Test")
        method = test.get("method", test_name)

        # Get failure details
        failure_elem = test.find("failure")
        error_output = ""
        if failure_elem is not None:
            exception_type = failure_elem.get("exception-type", "")
            message_elem = failure_elem.find("message")
            stack_trace_elem = failure_elem.find("stack-trace")

            message = message_elem.text if message_elem is not None else ""
            stack_trace = stack_trace_elem.text if stack_trace_elem is not None else ""

            error_output = f"{exception_type}: {message}\n{stack_trace}".strip()

        # Get execution time
        time = test.get("time", "0")
        try:
            execution_time = float(time)
        except ValueError:
            execution_time = 0.0

        return FailedCommand(
            title=f"xUnit Test: {method}",
            command=f"Test: {method}",
            source=source,
            command_type="xunit_test",
            status="Failed",
            return_code=1,
            execution_time=execution_time,
            output="",
            error_output=error_output,
            metadata={
                "test_name": test_name,
                "method": method,
                "type": test.get("type", ""),
                "result": test.get("result", ""),
            },
        )


class GenericXMLParser:
    """Generic XML parser for unknown formats."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse generic XML data."""
        commands = []

        # Search for elements that might indicate failures
        failure_indicators = [
            "failure",
            "error",
            "failed",
            "exception",
            "stderr",
            "fault",
            "issue",
        ]

        for indicator in failure_indicators:
            elements = root.findall(f".//{indicator}")
            for elem in elements:
                command = self._create_generic_command(elem, indicator, source)
                if command:
                    commands.append(command)

        return commands

    def _create_generic_command(
        self, elem: ET.Element, indicator: str, source: str
    ) -> Optional[FailedCommand]:
        """Create generic FailedCommand from XML element."""
        # Try to extract meaningful information
        text = elem.text or ""
        attribs = elem.attrib

        # Skip if element is empty
        if not text and not attribs:
            return None

        # Create title from element info
        title = f"XML {indicator.title()}"
        if "name" in attribs:
            title += f": {attribs['name']}"
        elif "id" in attribs:
            title += f": {attribs['id']}"

        # Extract command/test name
        command = attribs.get(
            "name", attribs.get("test", attribs.get("method", f"XML {indicator}"))
        )

        # Extract error details
        error_output = text
        if "message" in attribs:
            error_output = f"{attribs['message']}\n{text}".strip()

        return FailedCommand(
            title=title,
            command=str(command),
            source=source,
            command_type="generic_xml",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=error_output,
            metadata={
                "xml_tag": elem.tag,
                "xml_attributes": attribs,
                "indicator_type": indicator,
            },
        )


class MSBuildParser:
    """Parser for MSBuild XML logs."""

    def parse(self, root: ET.Element, source: str) -> List[FailedCommand]:
        """Parse MSBuild XML log."""
        commands = []

        # Find build errors
        for error in root.findall(".//error"):
            command = self._create_command_from_error(error, source)
            commands.append(command)

        # Find build warnings treated as errors
        for warning in root.findall(".//warning"):
            if warning.get("treatAsError", "false").lower() == "true":
                command = self._create_command_from_warning(warning, source)
                commands.append(command)

        return commands

    def _create_command_from_error(
        self, error: ET.Element, source: str
    ) -> FailedCommand:
        """Create FailedCommand from MSBuild error."""
        code = error.get("code", "Unknown")
        file_path = error.get("file", "")
        line = error.get("line", "")
        message = error.text or "No error message"

        title = f"MSBuild Error {code}"
        if file_path:
            title += f" in {Path(file_path).name}"

        command = f"MSBuild compile {file_path}" if file_path else "MSBuild compile"

        error_output = f"Error {code}: {message}"
        if line:
            error_output += f" (line {line})"

        return FailedCommand(
            title=title,
            command=command,
            source=source,
            command_type="msbuild_error",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=error_output,
            metadata={
                "error_code": code,
                "file_path": file_path,
                "line_number": line,
                "column": error.get("column", ""),
            },
        )

    def _create_command_from_warning(
        self, warning: ET.Element, source: str
    ) -> FailedCommand:
        """Create FailedCommand from MSBuild warning treated as error."""
        code = warning.get("code", "Unknown")
        file_path = warning.get("file", "")
        message = warning.text or "No warning message"

        title = f"MSBuild Warning-as-Error {code}"
        if file_path:
            title += f" in {Path(file_path).name}"

        return FailedCommand(
            title=title,
            command=f"MSBuild compile {file_path}" if file_path else "MSBuild compile",
            source=source,
            command_type="msbuild_warning_error",
            status="Failed",
            return_code=1,
            execution_time=0.0,
            output="",
            error_output=f"Warning treated as error {code}: {message}",
            metadata={
                "warning_code": code,
                "file_path": file_path,
                "treated_as_error": True,
            },
        )
