# this_file: src/twat_fs/upload_providers/utils.py

"""
Shared utilities for upload providers.
Contains common functionality used across multiple providers to reduce code duplication.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    TypeVar,
    ParamSpec,
    TYPE_CHECKING,
)
from collections.abc import Generator
import aiohttp
import requests
from loguru import logger

from twat_fs.upload_providers.core import (
    RetryableError,
    NonRetryableError,
)
from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.types import UploadResult

if TYPE_CHECKING:
    from twat_fs.upload_providers.protocols import Provider

# Type variables for generic functions
T = TypeVar("T")
P = ParamSpec("P")


def create_provider_help(
    setup_instructions: str,
    dependency_info: str,
) -> ProviderHelp:
    """
    Create a standardized provider help dictionary.

    Args:
        setup_instructions: Instructions for setting up the provider
        dependency_info: Information about provider dependencies

    Returns:
        ProviderHelp: Standardized help dictionary
    """
    return {
        "setup": setup_instructions,
        "deps": dependency_info,
    }


@contextmanager
def safe_file_handle(file_path: str | Path) -> Generator[BinaryIO]:
    """
    Safely open and manage a file handle for upload.

    Args:
        file_path: Path to the file to open

    Yields:
        BinaryIO: Open file handle in binary mode

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        ValueError: If path is not a file
    """
    path = Path(str(file_path))
    validate_file(path)

    file: BinaryIO | None = None
    try:
        file = open(path, "rb")
        yield file
    finally:
        if file:
            file.close()


def validate_file(file_path: Path) -> None:
    """
    Validate that a file exists and is readable.

    Args:
        file_path: Path to validate

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read
        ValueError: If path is not a file
    """
    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)
    if not file_path.is_file():
        msg = f"Not a file: {file_path}"
        raise ValueError(msg)
    if not os.access(file_path, os.R_OK):
        msg = f"Cannot read file: {file_path}"
        raise PermissionError(msg)


def handle_http_response(
    response: requests.Response | aiohttp.ClientResponse,
    provider_name: str,
) -> None:
    """
    Handle HTTP response status codes consistently.

    Args:
        response: HTTP response object
        provider_name: Name of the provider for error messages

    Raises:
        RetryableError: For temporary failures (e.g., rate limits)
        NonRetryableError: For permanent failures
    """
    status_code = (
        response.status
        if isinstance(response, aiohttp.ClientResponse)
        else response.status_code
    )

    if status_code == 429:
        msg = f"Rate limited: {response.text if isinstance(response, requests.Response) else 'Too many requests'}"
        raise RetryableError(msg, provider_name)
    elif status_code == 503:
        msg = "Service temporarily unavailable"
        raise RetryableError(msg, provider_name)
    elif status_code in (400, 401, 403, 404):
        msg = f"Request failed with status {status_code}"
        raise NonRetryableError(msg, provider_name)
    elif status_code != 200:
        msg = f"Request failed with status {status_code}"
        raise RetryableError(msg, provider_name)


def get_env_credentials(
    required_vars: list[str],
    optional_vars: list[str] | None = None,
) -> dict[str, str] | None:
    """
    Get credentials from environment variables.

    Args:
        required_vars: List of required environment variable names
        optional_vars: List of optional environment variable names

    Returns:
        Optional[Dict[str, str]]: Credentials dictionary or None if required vars missing
    """
    optional_vars = optional_vars or []
    creds: dict[str, str] = {}

    # Check required variables
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.debug(f"Missing required environment variables: {', '.join(missing)}")
        return None

    # Collect all variables
    for var in required_vars + optional_vars:
        if value := os.getenv(var):
            creds[var] = value

    return creds


def create_provider_instance(
    provider_class: type[Provider], credentials: dict[str, Any] | None = None
) -> ProviderClient | None:
    """
    Create an instance of a provider class.

    This function will try to create an instance of a provider class in the following order:
    1. If the provider class has a get_provider method, use that
    2. If credentials are provided, use them to instantiate the provider
    3. If no credentials are provided, try to get them from the provider class
    4. If all else fails, instantiate the provider without credentials

    Args:
        provider_class: The provider class to instantiate
        credentials: Optional credentials to use for instantiation

    Returns:
        An instance of the provider class, or None if instantiation fails
    """
    provider_name = getattr(provider_class, "__name__", "Unknown")

    try:
        # If no credentials are provided, try to get them from the provider class
        if credentials is None and hasattr(provider_class, "get_credentials"):
            credentials = provider_class.get_credentials()

        # Check if the provider class has a get_provider method
        if hasattr(provider_class, "get_provider"):
            try:
                return provider_class.get_provider()
            except (AttributeError, TypeError):
                # If get_provider fails, continue with direct instantiation
                pass

        # Try direct instantiation
        return provider_class()
    except Exception as e:
        logger.error(f"Failed to initialize provider {provider_name}: {e}")
        return None


def standard_upload_wrapper(
    provider: ProviderClient | None,
    provider_name: str,
    local_path: str | Path,
    remote_path: str | Path | None = None,
    **kwargs: Any,
) -> UploadResult:
    """
    Standard wrapper for upload_file functions.

    Args:
        provider: Provider instance
        provider_name: Name of the provider for error messages
        local_path: Path to file to upload
        remote_path: Optional remote path
        **kwargs: Additional provider-specific arguments

    Returns:
        UploadResult: Upload result with URL and metadata

    Raises:
        ValueError: If provider initialization fails
    """
    if not provider:
        msg = f"Failed to initialize {provider_name} provider"
        raise ValueError(msg)

    return provider.upload_file(local_path, remote_path, **kwargs)


def log_upload_attempt(
    provider_name: str,
    file_path: str | Path,
    success: bool,
    error: Exception | None = None,
) -> None:
    """
    Standardized logging for upload attempts.

    Args:
        provider_name: Name of the provider
        file_path: Path to the file being uploaded
        success: Whether the upload succeeded
        error: Optional exception if upload failed
    """
    if success:
        logger.info(f"Successfully uploaded {file_path} using {provider_name}")
    else:
        logger.error(f"Failed to upload {file_path} using {provider_name}: {error}")
