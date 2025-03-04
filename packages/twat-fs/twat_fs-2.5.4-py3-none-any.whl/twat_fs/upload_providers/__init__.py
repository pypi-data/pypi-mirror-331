# this_file: src/twat_fs/upload_providers/__init__.py

"""
Upload provider registry and base classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from twat_fs.upload_providers.core import RetryableError, NonRetryableError, UploadError
from twat_fs.upload_providers.protocols import ProviderClient, Provider, ProviderHelp
from twat_fs.upload_providers.types import ExpirationTime, UploadResult
from twat_fs.upload_providers.factory import ProviderFactory

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
    "ProviderFactory",
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

    This function is maintained for backward compatibility.
    New code should use ProviderFactory.get_provider_module() instead.

    Args:
        provider: Name of the provider to get

    Returns:
        Optional[Provider]: Provider module if found and properly configured
    """
    return ProviderFactory.get_provider_module(provider)


def get_provider_help(provider: str) -> ProviderHelp | None:
    """
    Get help information for a provider.

    This function is maintained for backward compatibility.
    New code should use ProviderFactory.get_provider_help() instead.

    Args:
        provider: Name of the provider to get help for

    Returns:
        Optional[ProviderHelp]: Help information if provider exists
    """
    return ProviderFactory.get_provider_help(provider)
