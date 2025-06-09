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
            error_details = failure_elem
