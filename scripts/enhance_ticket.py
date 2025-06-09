#!/usr/bin/env python3
"""
Script to enhance a GitHub issue with more detailed information using local LLM.
"""
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdiss.ai.ticket_generator import AITicketGenerator


def enhance_ticket(title: str, command: str, error_output: str = "") -> dict:
    """Enhance ticket with more detailed information using LLM."""
    prompt = f"""
    Analyze the following test failure and enhance the ticket with more details:

    Title: {title}

    Command that failed:
    ```
    {command}
    ```

    Error output:
    ```
    {error_output if error_output else 'No error output available'}
    ```

    Please provide a detailed analysis including:
    1. Possible causes of the failure
    2. Steps to reproduce
    3. Expected vs actual behavior
    4. Suggested solutions or debugging steps
    5. Any relevant code context needed

    Format the response in clear markdown sections.
    """

    generator = AITicketGenerator()
    enhanced_description = generator.generate_enhanced_description(prompt)

    return {
        "title": title,
        "description": enhanced_description,
        "labels": ["bug", "test-failure", "priority:high"],
        "command": command,
        "error_output": error_output,
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python enhance_ticket.py <title> <command> [error_output_file]")
        sys.exit(1)

    title = sys.argv[1]
    command = sys.argv[2]
    error_output = ""

    if len(sys.argv) > 3:
        try:
            with open(sys.argv[3], "r") as f:
                error_output = f.read()
        except Exception as e:
            print(f"Error reading error output file: {e}")

    enhanced = enhance_ticket(title, command, error_output)
    print(json.dumps(enhanced, indent=2))


if __name__ == "__main__":
    main()
