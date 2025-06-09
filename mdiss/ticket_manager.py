"""Unified interface for markdown processing and issue tracker integration."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from .ai.ticket_generator import (
    AITicketGenerator,
    generate_github_issue,
    generate_gitlab_issue,
)
from .integrations import GitHubIntegration, GitLabIntegration, get_integration
from .parser.markdown_processor import MarkdownProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TicketManager:
    """Manages tickets across different platforms with markdown support."""

    def __init__(
        self,
        markdown_path: Optional[Union[str, Path]] = None,
        provider: str = "github",
        llm_model: str = "mistral:7b",
        ollama_host: str = "http://localhost:11434",
        **integration_kwargs,
    ):
        """Initialize the ticket manager with local LLM support.

        Args:
            markdown_path: Path to a markdown file or directory
            provider: Default issue tracker provider ('github' or 'gitlab')
            llm_model: Name of the Ollama model to use (default: 'mistral:7b')
            ollama_host: Base URL for Ollama API
            **integration_kwargs: Arguments for the integration (e.g., token, api_key)
        """
        self.markdown_processor = None
        if markdown_path:
            self.markdown_processor = MarkdownProcessor(file_path=markdown_path)

        self.provider = provider.lower()
        self.integration = get_integration(provider, **integration_kwargs)

        # Initialize the local LLM
        try:
            self.ai_generator = AITicketGenerator(
                model=llm_model, ollama_host=ollama_host
            )
            logger.info(f"Initialized local LLM with model: {llm_model}")
        except Exception as e:
            logger.error(f"Failed to initialize local LLM: {e}")
            raise

    def extract_tickets(self) -> List[Dict[str, Any]]:
        """Extract ticket information from markdown content.

        Returns:
            List of extracted ticket data
        """
        if not self.markdown_processor:
            return []

        tickets = []
        headings = self.markdown_processor.extract_headings(
            level=2
        )  # Assuming tickets are h2

        for heading in headings:
            # Extract content between h2 headings as ticket content
            ticket_data = {
                "title": heading["text"],
                "description": "",  # TODO: Extract content until next h2
                "labels": self._extract_labels(heading["text"]),
                "metadata": self._extract_metadata(heading["text"]),
            }
            tickets.append(ticket_data)

        return tickets

    def create_ticket(
        self,
        title: str,
        description: str,
        labels: Optional[List[str]] = None,
        use_ai: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new ticket in the configured issue tracker.

        Args:
            title: Ticket title
            description: Ticket description
            labels: List of labels
            use_ai: Whether to use AI to enhance the ticket
            **kwargs: Additional arguments for the ticket

        Returns:
            Created ticket data
        """
        if use_ai:
            if self.provider == "github":
                ticket_data = generate_github_issue(
                    title=title, description=description, labels=labels, **kwargs
                )
            else:  # gitlab
                ticket_data = generate_gitlab_issue(
                    title=title, description=description, labels=labels, **kwargs
                )
        else:
            ticket_data = {
                "title": title,
                "description": description,
                "labels": labels or [],
                **kwargs,
            }

        # Create the ticket using the appropriate integration
        if self.provider == "github":
            result = self.integration.create_issue(
                title=ticket_data["title"],
                body=ticket_data.get("description", ""),
                labels=ticket_data.get("labels", []),
                **{
                    k: v
                    for k, v in ticket_data.items()
                    if k not in ["title", "description", "labels"]
                },
            )
        else:  # gitlab
            result = self.integration.create_issue(
                project_id=kwargs.get("project_id"),
                title=ticket_data["title"],
                description=ticket_data.get("description", ""),
                labels=ticket_data.get("labels", []),
                **{
                    k: v
                    for k, v in ticket_data.items()
                    if k not in ["project_id", "title", "description", "labels"]
                },
            )

        return result

    def update_ticket(self, ticket_id: Union[int, str], **updates) -> Dict[str, Any]:
        """Update an existing ticket.

        Args:
            ticket_id: ID or IID of the ticket
            **updates: Fields to update

        Returns:
            Updated ticket data
        """
        if self.provider == "github":
            return self.integration.update_issue(issue_number=ticket_id, **updates)
        else:  # gitlab
            return self.integration.update_issue(issue_iid=ticket_id, **updates)

    def list_tickets(self, state: str = "open", **filters) -> List[Dict[str, Any]]:
        """List tickets from the issue tracker.

        Args:
            state: Ticket state ('open', 'closed', 'all')
            **filters: Additional filters

        Returns:
            List of tickets
        """
        if self.provider == "github":
            return self.integration.list_issues(state=state, **filters)
        else:  # gitlab
            return self.integration.list_issues(state=state, **filters)

    def _extract_labels(self, text: str) -> List[str]:
        """Extract labels from text.

        Args:
            text: Text to extract labels from

        Returns:
            List of labels
        """
        # Simple implementation - can be enhanced with regex or AI
        labels = []
        if "bug" in text.lower():
            labels.append("bug")
        if "feature" in text.lower():
            labels.append("enhancement")
        if "docs" in text.lower():
            labels.append("documentation")

        return labels

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text.

        Args:
            text: Text to extract metadata from

        Returns:
            Dictionary of metadata
        """
        # Simple implementation - can be enhanced with regex or AI
        metadata = {}
        if "critical" in text.lower():
            metadata["priority"] = "high"
        if "low" in text.lower():
            metadata["priority"] = "low"

        return metadata


def create_ticket_from_markdown(
    markdown_path: Union[str, Path], provider: str = "github", **kwargs
) -> Dict[str, Any]:
    """Create a ticket from a markdown file.

    Args:
        markdown_path: Path to the markdown file
        provider: Issue tracker provider ('github' or 'gitlab')
        **kwargs: Additional arguments for the ticket

    Returns:
        Created ticket data
    """
    manager = TicketManager(markdown_path=markdown_path, provider=provider, **kwargs)
    tickets = manager.extract_tickets()

    if not tickets:
        raise ValueError("No tickets found in the markdown file")

    # Create the first ticket found
    ticket = tickets[0]
    return manager.create_ticket(
        title=ticket["title"],
        description=ticket.get("description", ""),
        labels=ticket.get("labels", []),
        **ticket.get("metadata", {}),
    )
