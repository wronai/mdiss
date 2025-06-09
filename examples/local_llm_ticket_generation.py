#!/usr/bin/env python3
"""
Example script demonstrating local LLM-powered ticket generation using Mistral 7B via Ollama.

Make sure Ollama is running and the Mistral 7B model is available before running this script.

To run this example:
1. Ensure Ollama is installed and running (https://ollama.ai/)
2. Pull the Mistral model: `ollama pull mistral:7b`
3. Run this script: `python examples/local_llm_ticket_generation.py`
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdiss.ai.ticket_generator import (
    AITicketGenerator,
    generate_github_issue,
    generate_gitlab_issue,
)


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 80}")
    print(f"{title.upper():^80}")
    print(f"{'=' * 80}")


def print_json(data: Dict[str, Any], title: Optional[str] = None):
    """Print JSON data with an optional title."""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_basic_generation():
    """Test basic ticket generation with the local LLM."""
    print_header("Testing Basic Ticket Generation")

    # Initialize the ticket generator with default settings
    generator = AITicketGenerator()

    # Define ticket details
    title = "Fix login page layout issues on mobile devices"
    description = """The login page has several layout issues on mobile devices:

    1. The login form overflows on smaller screens
    2. The submit button is not properly aligned
    3. Error messages are cut off on the right side

    This affects all mobile users trying to access the application."""

    # Generate the ticket
    print("Generating ticket with local LLM...")
    ticket = generator.generate_ticket(title, description)

    # Print the result
    print_json(ticket, "Generated Ticket")


def test_github_issue_generation():
    """Test GitHub issue generation with the local LLM."""
    print_header("Testing GitHub Issue Generation")

    # Define GitHub issue details
    title = "Add dark mode support"
    description = """We should add a dark mode to improve user experience in low-light conditions.

    Requirements:
    - Toggle between light and dark themes
    - Respect system preferences
    - Ensure good contrast ratios for accessibility
    - Update documentation"""

    # Generate a GitHub issue
    print("Generating GitHub issue with local LLM...")
    issue = generate_github_issue(
        title=title,
        description=description,
        labels=["enhancement", "ui/ux"],
        assignees=["dev1"],
        model="mistral:7b",  # Explicitly specify the model
    )

    # Print the result
    print_json(issue, "Generated GitHub Issue")


def test_gitlab_issue_generation():
    """Test GitLab issue generation with the local LLM."""
    print_header("Testing GitLab Issue Generation")

    # Define GitLab issue details
    title = "Implement password strength meter"
    description = """We need to add a password strength meter to the registration form.

    Acceptance criteria:
    - Show password strength as user types
    - Enforce minimum password requirements
    - Provide feedback on how to improve password strength
    - Support i18n for feedback messages"""

    # Generate a GitLab issue
    print("Generating GitLab issue with local LLM...")
    issue = generate_gitlab_issue(
        title=title,
        description=description,
        labels=["enhancement", "security"],
        assignee_ids=[42],  # Example user ID
        model="mistral:7b",  # Explicitly specify the model
    )

    # Print the result
    print_json(issue, "Generated GitLab Issue")


def test_custom_model():
    """Test using a custom model with the ticket generator."""
    print_header("Testing Custom Model")

    # Initialize with a different model (e.g., llama2)
    try:
        print("Initializing with custom model...")
        generator = AITicketGenerator(model="llama2")

        # Generate a simple ticket
        print("Generating ticket with custom model...")
        ticket = generator.generate_ticket(
            title="Update documentation",
            description="We need to update the API documentation to reflect recent changes.",
        )

        print_json(ticket, "Ticket from Custom Model")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the specified model is available in Ollama.")


def main():
    """Run all the test cases."""
    try:
        test_basic_generation()
        test_github_issue_generation()
        test_gitlab_issue_generation()
        test_custom_model()

        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Ollama is running and the Mistral 7B model is available.")
        print("You can install it with: ollama pull mistral:7b")
        sys.exit(1)


if __name__ == "__main__":
    main()
