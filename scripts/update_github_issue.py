#!/usr/bin/env python3
"""
Script to update a GitHub issue with enhanced description using local LLM.
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def update_github_issue(
    owner: str,
    repo: str,
    issue_number: int,
    token: str,
    title: Optional[str] = None,
    body: Optional[str] = None,
    labels: Optional[list] = None,
) -> Dict[str, Any]:
    """Update a GitHub issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number to update
        token: GitHub personal access token
        title: New issue title (optional)
        body: New issue body (optional)
        labels: List of labels (optional)

    Returns:
        Dict with the updated issue data
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {}
    if title:
        data["title"] = title
    if body:
        data["body"] = body
    if labels is not None:
        data["labels"] = labels

    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def main():
    if len(sys.argv) < 5:
        print(
            "Usage: python update_github_issue.py <owner> <repo> <issue_number> <enhanced_ticket.json>"
        )
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    issue_number = int(sys.argv[3])
    enhanced_ticket_file = sys.argv[4]

    # Get GitHub token from environment
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    # Load enhanced ticket data
    try:
        with open(enhanced_ticket_file, "r") as f:
            enhanced_ticket = json.load(f)
    except Exception as e:
        print(f"Error loading enhanced ticket file: {e}")
        sys.exit(1)

    # Update the GitHub issue
    try:
        updated_issue = update_github_issue(
            owner=owner,
            repo=repo,
            issue_number=issue_number,
            token=token,
            title=enhanced_ticket.get("title"),
            body=enhanced_ticket.get("description"),
            labels=enhanced_ticket.get("labels"),
        )
        print(f"Successfully updated issue #{issue_number}")
        print(f"URL: {updated_issue.get('html_url')}")
    except Exception as e:
        print(f"Error updating issue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
