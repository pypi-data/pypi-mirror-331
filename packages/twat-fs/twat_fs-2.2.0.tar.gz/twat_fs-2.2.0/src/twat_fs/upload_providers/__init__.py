# this_file: src/twat_fs/upload_providers/__init__.py

"""
Upload provider registry and base classes.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, cast

from loguru import logger

from twat_fs.upload_providers.core import RetryableError, NonRetryableError, UploadError
from twat_fs.upload_providers.protocols import ProviderClient, Provider, ProviderHelp
from twat_fs.upload_providers.types import ExpirationTime, UploadResult

if TYPE_CHECKING:
    from pathlib import Path

# List of available providers in order of preference
PROVIDERS_PREFERENCE = [
    "litterbox",
    "bashupload",
    "www0x0",
    "uguu",
    "fal",
    "s3",
    "dropbox",
    "catbox",
    "filebin",
]

__all__ = [
    "PROVIDERS_PREFERENCE",
    "ExpirationTime",
    "NonRetryableError",
    "Provider",
    "ProviderClient",
    "ProviderHelp",
    "RetryableError",
    "UploadError",
    "UploadResult",
    "get_provider_help",
    "get_provider_module",
]


def get_provider_module(provider: str) -> Provider | None:
    """
    Get the provider module for a given provider name.

    Args:
        provider: Name of the provider to get

    Returns:
        Optional[Provider]: Provider module if found and properly configured
    """
    try:
        # Skip the 'simple' provider as it's just a base class
        if provider.lower() == "simple":
            return None

        # Try to import the module
        try:
            module = importlib.import_module(f".{provider}", __package__)
        except ImportError as e:
            if "No module named" in str(e):
                logger.debug(f"Provider module {provider} not found")
            else:
                logger.warning(f"Error importing provider {provider}: {e}")
            return None

        # Verify the module implements the Provider protocol
        required_attrs = ["get_provider", "get_credentials", "upload_file"]
        missing_attrs = [attr for attr in required_attrs if not hasattr(module, attr)]

        if missing_attrs:
            logger.warning(
                f"Provider {provider} is missing required attributes: {', '.join(missing_attrs)}"
            )
            return None

        # Check for provider help
        if not hasattr(module, "PROVIDER_HELP"):
            logger.warning(f"Provider {provider} is missing help information")
            return None

        return cast(Provider, module)

    except Exception as e:
        logger.error(f"Unexpected error loading provider {provider}: {e}")
        return None


def get_provider_help(provider: str) -> ProviderHelp | None:
    """
    Get help information for a provider.

    Args:
        provider: Name of the provider to get help for

    Returns:
        Optional[ProviderHelp]: Help information if provider exists
    """
    try:
        # Skip the 'simple' provider
        if provider.lower() == "simple":
            return {
                "setup": "This is a base provider and should not be used directly.",
                "deps": "None",
            }

        # Try to get the module
        module = get_provider_module(provider)
        if module is None:
            # Try to import just for help info
            try:
                module = importlib.import_module(f".{provider}", __package__)
                return getattr(module, "PROVIDER_HELP", None)
            except ImportError:
                return None

        return getattr(module, "PROVIDER_HELP", None)

    except Exception as e:
        logger.error(f"Error getting help for provider {provider}: {e}")
        return None
