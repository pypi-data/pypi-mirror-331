# this_file: src/twat_fs/upload_providers/fal.py

"""
FAL provider for file uploads.
This module provides functionality to upload files to FAL's storage service.
"""

from __future__ import annotations
from typing import Any, BinaryIO, ClassVar, cast
from pathlib import Path

import fal_client  # type: ignore
from loguru import logger  # type: ignore

from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.core import (
    RetryableError,
    NonRetryableError,
    convert_to_upload_result,
)
from twat_fs.upload_providers.utils import (
    create_provider_help,
    get_env_credentials,
    log_upload_attempt,
    standard_upload_wrapper,
)
from twat_fs.upload_providers.types import UploadResult

# Provider-specific help messages
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="""To use FAL storage:
1. Create a FAL account at https://fal.ai
2. Generate an API key from your account settings
3. Set the following environment variable:
   - FAL_KEY: Your FAL API key""",
    dependency_info="""Additional setup needed:
1. Install the FAL client: pip install fal-client
2. Ensure your API key has the necessary permissions""",
)


class FalProvider(BaseProvider):
    """Provider for uploading files to FAL."""

    # Class variables
    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name = "fal"

    # Environment variables
    REQUIRED_ENV_VARS = ["FAL_KEY"]
    OPTIONAL_ENV_VARS: list[str] = []

    def __init__(self, key: str) -> None:
        """Initialize the FAL provider with the given API key."""
        super().__init__()
        self.key = key
        self.client = self._create_client()

    def _create_client(self) -> Any:
        """Create and return a FAL client instance."""
        try:
            return fal_client.SyncClient(key=self.key)
        except Exception as e:
            logger.error(f"Failed to create FAL client: {e}")
            msg = f"Failed to create FAL client: {e}"
            raise NonRetryableError(msg, self.provider_name)

    @classmethod
    def get_credentials(cls) -> dict[str, str] | None:
        """
        Fetch FAL credentials from environment.

        Returns:
            dict[str, str] | None: Dictionary with FAL key if present, None otherwise
        """
        creds = get_env_credentials(cls.REQUIRED_ENV_VARS, cls.OPTIONAL_ENV_VARS)
        if not creds:
            return None

        return {"key": creds["FAL_KEY"]}

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """
        Initialize and return the FAL provider if credentials are present.

        Returns:
            Optional[ProviderClient]: FAL provider instance if credentials are present, None otherwise
        """
        creds = cls.get_credentials()
        if not creds:
            logger.debug("FAL_KEY not set in environment")
            return None

        try:
            # Ensure the key is a clean string by stripping whitespace
            provider = cls(key=str(creds["key"]).strip())
            return cast(ProviderClient, provider)
        except Exception as err:
            logger.warning(f"Failed to initialize FAL provider: {err}")
            return None

    def _do_upload(self, file: BinaryIO) -> str:
        """
        Internal method to handle the actual upload to FAL.

        Args:
            file: Open file handle to upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        # Verify FAL client is properly initialized
        if not hasattr(self.client, "upload_file"):
            msg = "FAL client not properly initialized"
            raise NonRetryableError(msg, self.provider_name)

        # Check if FAL key is still valid
        try:
            # Just try to access a property that requires auth
            _ = self.client.key
            logger.debug("FAL: API credentials verified")
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                msg = "FAL API key is invalid or expired. Please generate a new key."
                raise NonRetryableError(msg, self.provider_name) from e
            msg = f"FAL API check failed: {e}"
            raise RetryableError(msg, self.provider_name) from e

        try:
            # Try uploading the file directly
            result = self.client.upload_file(file)

            if not result:
                msg = "FAL upload failed - no URL in response"
                raise RetryableError(msg, self.provider_name) from None

            result_str = str(result).strip()
            if not result_str:
                msg = "FAL upload failed - empty URL in response"
                raise RetryableError(msg, self.provider_name) from None

            return result_str

        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                msg = f"FAL upload failed - unauthorized: {e}"
                raise NonRetryableError(msg, self.provider_name) from e
            msg = f"FAL upload failed: {e}"
            raise RetryableError(msg, self.provider_name) from e

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult: Upload result with URL and metadata

        Raises:
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        try:
            url = self._do_upload(file)
            log_upload_attempt(self.provider_name, file.name, success=True)

            return convert_to_upload_result(
                url,
                metadata={
                    "provider": self.provider_name,
                    "success": True,
                },
            )
        except Exception as e:
            log_upload_attempt(self.provider_name, file.name, success=False, error=e)
            raise


# Module-level functions that delegate to the FalProvider class
def get_credentials() -> dict[str, str] | None:
    """
    Get FAL credentials from environment.
    Delegates to FalProvider.get_credentials().
    """
    return FalProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """
    Initialize and return the FAL provider if credentials are present.
    Delegates to FalProvider.get_provider().
    """
    return FalProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
) -> UploadResult:
    """
    Upload a file using FAL.

    Args:
        local_path: Path to the file to upload
        remote_path: Optional remote path (ignored for FAL)
        unique: Whether to ensure unique filenames (ignored for FAL)
        force: Whether to overwrite existing files (ignored for FAL)
        upload_path: Base path for uploads (ignored for FAL)

    Returns:
        UploadResult: Upload result with URL and metadata

    Raises:
        FileNotFoundError: If the file doesn't exist
        RetryableError: For temporary failures that can be retried
        NonRetryableError: For permanent failures
        ValueError: If provider initialization fails
    """
    return standard_upload_wrapper(
        provider=get_provider(),
        provider_name="fal",
        local_path=local_path,
        remote_path=remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
