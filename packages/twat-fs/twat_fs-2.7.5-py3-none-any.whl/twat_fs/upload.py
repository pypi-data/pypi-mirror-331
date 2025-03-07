# this_file: src/twat_fs/upload.py

"""
Main upload module that provides a unified interface for uploading files
using different providers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto
import hashlib
import requests
import time

from loguru import logger

from twat_fs.upload_providers import (
    PROVIDERS_PREFERENCE,
    get_provider_help,
    get_provider_module,
    Provider,
    RetryableError,
    NonRetryableError,
    UploadResult,
    ProviderFactory,
)
from twat_fs.upload_providers.core import with_retry, RetryStrategy

if TYPE_CHECKING:
    from collections.abc import Sequence

# Type for provider specification - can be a single provider name or a list of providers
ProviderType = str | list[str] | None


class ProviderStatus(Enum):
    """Status of a provider's setup."""

    READY = auto()
    NEEDS_CONFIG = auto()
    NOT_AVAILABLE = auto()


@dataclass
class ProviderInfo:
    """Information about a provider's setup status."""

    success: bool
    explanation: str
    help_info: dict[str, str]
    timing: dict[str, float] | None = None


def _test_provider_online(
    provider_name: str,
) -> tuple[bool, str, dict[str, float] | None]:
    """
    Test a provider by uploading and downloading a small file.

    Args:
        provider_name: Name of the provider to test

    Returns:
        Tuple[bool, str, dict[str, float] | None]: (success, message, timing_metrics)
    """

    test_file = Path(__file__).parent / "data" / "test.jpg"
    if not test_file.exists():
        return False, f"Test file not found: {test_file}", None

    try:
        # Calculate original file hash
        with open(test_file, "rb") as f:
            original_hash = hashlib.sha256(f.read()).hexdigest()

        # Get the provider module and client using the factory
        provider_module = ProviderFactory.get_provider_module(provider_name)
        if not provider_module:
            return False, f"Provider module {provider_name} not found", None

        client = ProviderFactory.create_provider(provider_name)
        if not client:
            return False, f"Provider {provider_name} not configured", None

        # Track timing
        start_time = time.time()
        read_start = time.time()

        # Track file read time
        with open(test_file, "rb") as f:
            _ = f.read()  # Read file to measure read time
        read_duration = time.time() - read_start

        # Upload the file
        try:
            upload_start = time.time()
            result = client.upload_file(test_file)
            upload_duration = time.time() - upload_start

            if not result:
                end_time = time.time()
                timing_metrics: dict[str, float] = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "total_duration": end_time - start_time,
                    "read_duration": read_duration,
                    "upload_duration": upload_duration,
                    "validation_duration": 0.0,
                    "provider": float(hash(provider_name)),
                }
                return False, "Upload failed", timing_metrics

            # Extract URL and timing metrics
            if isinstance(result, UploadResult):
                url = result.url
                timing_metrics = result.metadata.get("timing", {})
            else:
                url = result
                timing_metrics = {}

            # Add a small delay to allow for propagation
            time.sleep(1.0)

            # Validate URL is accessible
            validation_start = time.time()
            response = requests.head(
                url,
                timeout=30,
                allow_redirects=True,
                headers={"User-Agent": "twat-fs/1.0"},
            )
            validation_duration = time.time() - validation_start

            if response.status_code not in (200, 201, 202, 203, 204):
                end_time = time.time()
                timing_metrics = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "total_duration": end_time - start_time,
                    "read_duration": read_duration,
                    "upload_duration": upload_duration,
                    "validation_duration": validation_duration,
                    "provider": float(hash(provider_name)),
                }
                return (
                    False,
                    f"URL validation failed: status {response.status_code}",
                    timing_metrics,
                )

        except ValueError as e:
            end_time = time.time()
            timing_metrics = {
                "start_time": start_time,
                "end_time": end_time,
                "total_duration": end_time - start_time,
                "read_duration": read_duration,
                "upload_duration": time.time() - upload_start,
                "validation_duration": 0.0,
                "provider": float(hash(provider_name)),
            }
            if "401" in str(e) or "authentication" in str(e).lower():
                return False, f"Authentication required: {e}", timing_metrics
            return False, f"Upload failed: {e}", timing_metrics
        except requests.RequestException as e:
            end_time = time.time()
            timing_metrics = {
                "start_time": start_time,
                "end_time": end_time,
                "total_duration": end_time - start_time,
                "read_duration": read_duration,
                "upload_duration": upload_duration,
                "validation_duration": time.time() - validation_start,
                "provider": float(hash(provider_name)),
            }
            return False, f"URL validation failed: {e}", timing_metrics

        # Download and verify the file with retries
        max_retries = 3
        retry_delay = 2  # seconds
        last_error = None
        time.time()

        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    # Calculate downloaded content hash
                    downloaded_hash = hashlib.sha256(response.content).hexdigest()

                    # Compare hashes
                    if original_hash == downloaded_hash:
                        end_time = time.time()
                        if not timing_metrics:
                            timing_metrics = {
                                "start_time": start_time,
                                "end_time": end_time,
                                "total_duration": end_time - start_time,
                                "read_duration": read_duration,
                                "upload_duration": upload_duration,
                                "validation_duration": validation_duration,
                                "provider": float(hash(provider_name)),
                            }
                        return True, "Online test passed successfully", timing_metrics
                    else:
                        last_error = f"Content verification failed: original {original_hash}, downloaded {downloaded_hash}"
                else:
                    last_error = f"Download failed with status {response.status_code}"

                # If we're not on the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
            except Exception as e:
                last_error = f"Download attempt {attempt + 1} failed: {e}"
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2

        end_time = time.time()
        if not timing_metrics:
            timing_metrics = {
                "start_time": start_time,
                "end_time": end_time,
                "total_duration": end_time - start_time,
                "read_duration": read_duration,
                "upload_duration": upload_duration,
                "validation_duration": validation_duration,
                "provider": float(hash(provider_name)),
            }
        return False, last_error or "Download failed after retries", timing_metrics

    except Exception as e:
        end_time = time.time()
        timing_metrics = {
            "start_time": start_time,
            "end_time": end_time,
            "total_duration": end_time - start_time,
            "read_duration": 0.0,
            "upload_duration": 0.0,
            "validation_duration": 0.0,
            "provider": float(hash(provider_name)),
        }
        return False, f"Unexpected error: {e}", timing_metrics


def setup_provider(
    provider: str, verbose: bool = False, online: bool = False
) -> ProviderInfo:
    """
    Check a provider's setup status and return its information.

    Args:
        provider: Name of the provider to check
        verbose: Whether to include detailed setup instructions
        online: Whether to perform an online test

    Returns:
        ProviderInfo: Provider status information
    """
    try:
        # Skip the 'simple' provider as it's just a base class
        if provider.lower() == "simple":
            return ProviderInfo(
                False,
                f"Provider '{provider}' is not available.",
                {},
            )

        # Import provider module
        provider_module = get_provider_module(provider)
        if not provider_module:
            help_info = get_provider_help(provider)
            if not help_info:
                return ProviderInfo(
                    False,
                    f"Provider '{provider}' is not available.",
                    {},
                )
            setup_info = help_info.get("setup", "")
            return ProviderInfo(
                False,
                f"Provider '{provider}' is not available.",
                {"setup": setup_info},
            )

        # Get help info for notes about retention
        help_info = get_provider_help(provider)
        retention_note = ""
        if help_info:
            setup_info = help_info.get("setup", "").lower()
            if "no setup required" in setup_info:
                # Extract any retention information
                if "deleted after" in setup_info or "only works with" in setup_info:
                    retention_note = setup_info[setup_info.find("note:") :].strip()

        # Try to get provider client
        try:
            client = provider_module.get_provider()
            if not client:
                setup_info = help_info.get("setup", "") if help_info else ""
                return ProviderInfo(
                    False,
                    f"Provider '{provider}' needs configuration.",
                    {"setup": setup_info},
                )

            provider_class = client.__class__
            # Check if it's a provider with both async_upload_file and upload_file
            has_async = hasattr(client, "async_upload_file") and not getattr(
                provider_class.async_upload_file,
                "__isabstractmethod__",
                False,
            )
            has_sync = hasattr(client, "upload_file") and not getattr(
                provider_class.upload_file,
                "__isabstractmethod__",
                False,
            )

            # A provider is ready if it has either:
            # 1. Both async_upload_file and upload_file methods
            # 2. Just the upload_file method
            if (has_async and has_sync) or has_sync:
                provider_info = ProviderInfo(
                    True,
                    f"{provider} ({type(client).__name__})"
                    + (f" - {retention_note}" if retention_note else ""),
                    {},
                )
            else:
                setup_info = help_info.get("setup", "") if help_info else ""
                provider_info = ProviderInfo(
                    False,
                    f"Provider '{provider}' needs configuration.",
                    {"setup": setup_info},
                )

            if online and provider_info.success:
                online_status, message, timing = _test_provider_online(provider)
                if not online_status:
                    provider_info = ProviderInfo(
                        False,
                        message,
                        provider_info.help_info,
                        timing,  # Store timing even for failed tests
                    )
                else:
                    provider_info.timing = timing
                    provider_info.explanation = (
                        f"{provider_info.explanation}\nOnline test passed successfully"
                    )
                    logger.debug(
                        f"Provider {provider} online test passed with timing: {timing}"
                    )

            return provider_info

        except Exception as e:
            logger.error(f"Error setting up provider {provider}: {e}")
            setup_info = help_info.get("setup", "") if help_info else ""
            return ProviderInfo(
                False,
                f"Provider '{provider}' setup failed: {e}",
                {"setup": setup_info},
            )

    except Exception as e:
        logger.error(f"Unexpected error setting up provider {provider}: {e}")
        return ProviderInfo(
            False,
            f"Provider '{provider}' failed: {e}",
            {},
        )


def setup_providers(
    verbose: bool = False, online: bool = False
) -> dict[str, ProviderInfo]:
    """
    Check setup status for all providers.

    Args:
        verbose: If True, print detailed status information
        online: If True, test providers by uploading a test file

    Returns:
        dict[str, ProviderInfo]: Dictionary mapping provider names to their setup status
    """
    results: dict[str, ProviderInfo] = {}

    for provider in PROVIDERS_PREFERENCE:
        result = setup_provider(provider, verbose=verbose, online=online)
        results[provider] = result

    return results


def _get_provider_module(provider: str) -> Provider | None:
    """Get a provider module with error handling."""
    try:
        return ProviderFactory.get_provider_module(provider)
    except Exception as e:
        logger.error(f"Error getting provider module {provider}: {e}")
        return None


def _try_upload_with_provider(
    provider_name: str,
    file_path: str | Path,
    *,
    remote_path: str | Path | None = None,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
) -> UploadResult:
    """Try to upload a file with a specific provider."""
    # Initialize timing variables
    start_time = time.time()
    read_start = time.time()
    read_duration = 0.0
    upload_start = 0.0
    upload_duration = 0.0
    validation_start = 0.0
    validation_duration = 0.0

    try:
        # Get the provider module
        provider_module = _get_provider_module(provider_name)
        if not provider_module:
            return UploadResult(
                url="",
                metadata={
                    "provider": provider_name,
                    "success": False,
                    "error": f"Provider {provider_name} not found",
                },
            )

        # Create the provider using the factory
        provider = ProviderFactory.create_provider(provider_name)
        if not provider:
            return UploadResult(
                url="",
                metadata={
                    "provider": provider_name,
                    "success": False,
                    "error": f"Provider {provider_name} not configured",
                },
            )

        # Track file read time
        path = Path(str(file_path))
        if path.exists():
            with open(path, "rb") as f:
                _ = f.read()  # Read file to measure read time
        read_duration = time.time() - read_start

        # Track upload time
        upload_start = time.time()
        upload_result = provider.upload_file(
            file_path,
            remote_path,
            unique=unique,
            force=force,
            upload_path=upload_path,
        )
        upload_duration = time.time() - upload_start

        # Track validation time
        validation_start = time.time()
        url = (
            upload_result.url
            if isinstance(upload_result, UploadResult)
            else upload_result
        )
        try:
            response = requests.head(
                url,
                timeout=30,
                allow_redirects=True,
                headers={"User-Agent": "twat-fs/1.0"},
            )
            if response.status_code not in (200, 201, 202, 203, 204):
                logger.warning(f"URL validation failed: status {response.status_code}")
        except Exception as e:
            logger.warning(f"URL validation failed: {e}")
        validation_duration = time.time() - validation_start

        end_time = time.time()
        total_duration = end_time - start_time

        # Create timing metrics
        timing = {
            "start_time": start_time,
            "end_time": end_time,
            "total_duration": total_duration,
            "read_duration": read_duration,
            "upload_duration": upload_duration,
            "validation_duration": validation_duration,
            "provider": provider_name,
        }

        # Convert string result to UploadResult if needed
        result = (
            UploadResult(url=upload_result, metadata={"provider": provider_name})
            if isinstance(upload_result, str)
            else upload_result
        )

        # Add timing information
        result.metadata["timing"] = timing

        # Log timing information
        logger.info(
            f"Upload timing for {provider_name}: "
            f"total={total_duration:.2f}s, "
            f"read={read_duration:.2f}s, "
            f"upload={upload_duration:.2f}s, "
            f"validation={validation_duration:.2f}s"
        )

        return result
    except Exception as e:
        end_time = time.time()
        total_duration = end_time - start_time

        return UploadResult(
            url="",
            metadata={
                "provider": provider_name,
                "success": False,
                "error": f"Upload failed: {e}",
                "timing": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "total_duration": total_duration,
                    "read_duration": read_duration,
                    "upload_duration": upload_duration,
                    "validation_duration": validation_duration,
                    "provider": provider_name,
                },
            },
        )


def _try_next_provider(
    remaining_providers: Sequence[str],
    file_path: str | Path,
    *,
    remote_path: str | Path | None = None,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
    fragile: bool = False,
    tried_providers: set[str] | None = None,
) -> str:
    """
    Try to upload a file using the next available provider.

    Args:
        remaining_providers: List of providers to try
        file_path: Path to the file to upload
        remote_path: Optional remote path
        unique: If True, ensures unique filename
        force: If True, overwrites existing file
        upload_path: Custom upload path
        fragile: If True, don't try other providers on failure
        tried_providers: Set of providers that have been tried

    Returns:
        str: URL of the uploaded file

    Raises:
        ValueError: If no providers are available or all uploads fail
    """
    if not remaining_providers:
        msg = "No providers available"
        raise ValueError(msg)

    # Keep track of tried providers to avoid loops
    tried = tried_providers or set()

    # Try each provider in sequence
    for provider in remaining_providers:
        if provider in tried:
            continue

        tried.add(provider)
        try:
            result = _try_upload_with_provider(
                provider,
                file_path,
                remote_path=remote_path,
                unique=unique,
                force=force,
                upload_path=upload_path,
            )
            return result.url

        except ValueError as e:
            if fragile:
                raise
            logger.warning(f"Provider {provider} failed: {e}")
            continue

    msg = f"All providers failed: {', '.join(tried)}"
    raise ValueError(msg)


@with_retry(
    max_attempts=2,  # One retry before falling back to next provider
    strategy=RetryStrategy.EXPONENTIAL,
    exceptions=(RetryableError,),  # Only retry on RetryableError
)
def upload_file(
    file_path: str | Path,
    provider: str | Sequence[str] | None = None,
    *,
    remote_path: str | Path | None = None,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
    fragile: bool = False,
) -> str:
    """
    Upload a file using the specified provider(s) with fallback.

    Args:
        file_path: Path to the file to upload
        provider: Provider name or list of providers to try in order
        remote_path: Optional remote path to use
        unique: Whether to ensure unique filenames
        force: Whether to overwrite existing files
        upload_path: Base path for uploads
        fragile: If True, fail immediately without trying fallback providers

    Returns:
        str: URL to the uploaded file

    Raises:
        NonRetryableError: If all providers fail
        FileNotFoundError: If the file doesn't exist
        ValueError: If no valid providers are available
    """
    # Validate file exists
    path = Path(file_path)
    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)
    if not path.is_file():
        msg = f"{path} is a directory"
        raise ValueError(msg)

    # Determine provider list
    providers = []
    if provider:
        providers = [provider] if isinstance(provider, str) else list(provider)
    else:
        providers = PROVIDERS_PREFERENCE

    # Validate providers
    if not providers:
        msg = "No providers specified"
        raise ValueError(msg)
    for p in providers:
        if p not in PROVIDERS_PREFERENCE:
            msg = f"Invalid provider: {p}"
            raise ValueError(msg)

    try:
        # Try first provider with retry
        return _try_upload_with_provider(
            providers[0],
            file_path,
            remote_path=remote_path,
            unique=unique,
            force=force,
            upload_path=upload_path,
        ).url
    except (RetryableError, NonRetryableError) as e:
        if fragile or len(providers) == 1:
            msg = f"Provider {providers[0]} failed: {e}"
            raise NonRetryableError(msg, providers[0])

        # Try remaining providers with circular fallback
        logger.info(f"Provider {providers[0]} failed, trying alternatives")
        return _try_next_provider(
            providers[1:],
            file_path,
            remote_path=remote_path,
            unique=unique,
            force=force,
            upload_path=upload_path,
            fragile=fragile,
            tried_providers={providers[0]},
        )


def _try_upload_with_fallback(
    provider: str,
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
    tried_providers: set[str] | None = None,
    **kwargs: Any,
) -> UploadResult:
    """
    Try to upload a file with fallback to other providers.

    Args:
        provider: Provider to try first
        local_path: Path to the file to upload
        remote_path: Optional remote path to use
        unique: If True, ensures unique filename
        force: If True, overwrites existing file
        upload_path: Custom upload path
        tried_providers: Set of providers that have been tried
        **kwargs: Additional provider-specific arguments

    Returns:
        UploadResult: Upload result with URL and metadata

    Raises:
        RuntimeError: If all providers fail
    """
    # Track which providers we've tried
    tried = tried_providers or set()
    tried.add(provider)

    try:
        # Try the current provider
        return _try_upload_with_provider(
            provider,
            local_path,
            remote_path=remote_path,
            unique=unique,
            force=force,
            upload_path=upload_path,
            **kwargs,
        )
    except Exception as e:
        logger.warning(f"Provider {provider} failed: {e}")

        # Try remaining providers in preference order
        remaining = [p for p in PROVIDERS_PREFERENCE if p not in tried]
        if not remaining:
            msg = "All providers failed"
            raise RuntimeError(msg) from None

        # Try next provider with fallback
        return _try_upload_with_fallback(
            remaining[0],
            local_path,
            remote_path=remote_path,
            unique=unique,
            force=force,
            upload_path=upload_path,
            tried_providers=tried,
            **kwargs,
        )
