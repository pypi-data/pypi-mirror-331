# this_file: src/twat_fs/upload_providers/www0x0.py

"""
0x0.st file upload provider.
A simple provider that uploads files to 0x0.st.
"""

from __future__ import annotations

import requests
from pathlib import Path
from typing import BinaryIO, ClassVar, cast

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
    setup_instructions="No setup required. Note: Files are stored permanently.",
    dependency_info="Python package: requests",
)


class Www0x0Provider(BaseProvider):
    """Provider for 0x0.st uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "www0x0"
    upload_url: str = "https://0x0.st"

    def __init__(self) -> None:
        """Initialize the 0x0.st provider."""
        self.provider_name = "www0x0"

    def _do_upload(self, file: BinaryIO) -> str:
        """
        Internal implementation of the file upload to 0x0.st.

        Args:
            file: Open file handle to upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting or temporary issues
            NonRetryableError: If the upload fails for any other reason
        """
        files = {"file": file}
        response = requests.post(self.upload_url, files=files, timeout=30)

        # Use standardized HTTP response handling
        handle_http_response(response, self.provider_name)

        # Parse the response
        url = response.text.strip()
        if not url.startswith("http"):
            msg = f"Invalid response from server: {url}"
            raise NonRetryableError(msg, self.provider_name)

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
    return Www0x0Provider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Return an instance of the provider"""
    return Www0x0Provider.get_provider()


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
        "www0x0",
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
