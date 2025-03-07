# this_file: src/twat_fs/upload_providers/uguu.py

"""
Uguu.se upload provider.
A simple provider that uploads files to uguu.se.
Files are automatically deleted after 48 hours.
"""

from __future__ import annotations

import requests
from pathlib import Path
from typing import BinaryIO, cast, ClassVar

from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.core import RetryableError, NonRetryableError
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.protocols import ProviderHelp, ProviderClient
from twat_fs.upload_providers.utils import (
    create_provider_help,
    handle_http_response,
    log_upload_attempt,
    standard_upload_wrapper,
)

# Use standardized provider help format
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="No setup required. Note: Files are deleted after 48 hours.",
    dependency_info="Python package: requests",
)


class UguuProvider(BaseProvider):
    """Provider for uguu.se uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "uguu"
    upload_url: str = "https://uguu.se/upload.php"

    def __init__(self) -> None:
        """Initialize the Uguu provider."""
        self.provider_name = "uguu"

    def _do_upload(self, file: BinaryIO) -> str:
        """
        Internal implementation of the file upload to uguu.se.

        Args:
            file: Open file handle to upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting or temporary issues
            NonRetryableError: If the upload fails for any other reason
        """
        files = {"files[]": file}
        response = requests.post(self.upload_url, files=files, timeout=30)

        # Use standardized HTTP response handling
        handle_http_response(response, self.provider_name)

        # Parse the response
        result = response.json()
        if not result or "files" not in result:
            msg = f"Invalid response from uguu.se: {result}"
            raise NonRetryableError(msg, self.provider_name)

        url = result["files"][0]["url"]
        return url

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # Upload the file
            url = self._do_upload(file)

            # Log successful upload
            log_upload_attempt(
                provider_name=self.provider_name,
                file_path=file.name,
                success=True,
            )

            return UploadResult(
                url=url,
                metadata={
                    "provider": self.provider_name,
                    "success": True,
                    "raw_url": url,
                },
            )
        except (RetryableError, NonRetryableError):
            # Re-raise these errors to allow for retries
            raise
        except Exception as e:
            # Log failed upload
            log_upload_attempt(
                provider_name=self.provider_name,
                file_path=file.name,
                success=False,
                error=e,
            )

            return UploadResult(
                url="",
                metadata={
                    "provider": self.provider_name,
                    "success": False,
                    "error": str(e),
                },
            )

    @classmethod
    def get_credentials(cls) -> None:
        """Simple providers don't need credentials"""
        return None

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """Initialize and return the provider client."""
        return cast(ProviderClient, cls())


# Module-level functions to implement the Provider protocol
def get_credentials() -> None:
    """Simple providers don't need credentials"""
    return UguuProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Return an instance of the provider"""
    return UguuProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
) -> UploadResult:
    """
    Upload a file and return its URL.

    Args:
        local_path: Path to the file to upload
        remote_path: Optional remote path (ignored for simple providers)
        unique: Ignored for this provider
        force: Ignored for this provider
        upload_path: Ignored for this provider

    Returns:
        UploadResult: URL of the uploaded file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a file
        PermissionError: If the file can't be read
        RuntimeError: If the upload fails
    """
    return standard_upload_wrapper(
        get_provider(),
        "uguu",
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
