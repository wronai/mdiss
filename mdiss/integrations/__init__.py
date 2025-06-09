"""Integration modules for issue trackers and other services."""
from typing import Any, Dict, Optional, Type

# Import integrations
from .github_integration import GitHubIntegration
from .gitlab_integration import GitLabIntegration

# Export integrations
__all__ = [
    "GitHubIntegration",
    "GitLabIntegration",
    "get_integration",
]


def get_integration(provider: str, **kwargs) -> Any:
    """Get an integration instance by provider name.

    Args:
        provider: Integration provider name ('github' or 'gitlab')
        **kwargs: Additional arguments for the integration

    Returns:
        An instance of the requested integration

    Raises:
        ValueError: If the provider is not supported
    """
    providers: Dict[str, Type] = {
        "github": GitHubIntegration,
        "gitlab": GitLabIntegration,
    }

    provider = provider.lower()
    if provider not in providers:
        raise ValueError(
            f"Unsupported provider: {provider}. Available providers: {', '.join(providers.keys())}"
        )

    return providers[provider](**kwargs)
