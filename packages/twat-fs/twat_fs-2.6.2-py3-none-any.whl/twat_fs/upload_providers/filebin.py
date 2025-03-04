# this_file: src/twat_fs/upload_providers/filebin.py

"""
Filebin.net upload provider.
A simple provider that uploads files to filebin.net.
Files are automatically deleted after 6 days.
"""

from __future__ import annotations

import requests
from pathlib import Path
from typing import BinaryIO, cast, ClassVar
import time
import secrets
import string

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
    setup_instructions="No setup required. Note: Files are deleted after 6 days.",
    dependency_info="Python package: requests",
)


class FilebinProvider(BaseProvider):
    """Provider for filebin.net uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "filebin"
    base_url: str = "https://filebin.net"

    def __init__(self) -> None:
        """Initialize the Filebin provider."""
        self.provider_name = "filebin"

    def _generate_bin_name(self) -> str:
        """
        Generate a unique bin name for filebin.net.

        Returns:
            str: A unique bin name
        """
        timestamp = int(time.time())
        suffix = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        )
        return f"twat-fs-{timestamp}-{suffix}"

    def _do_upload(self, file: BinaryIO, filename: str) -> str:
        """
        Internal implementation of the file upload to filebin.net.

        Args:
            file: Open file handle to upload
            filename: Name of the file to upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting or temporary issues
            NonRetryableError: If the upload fails for any other reason
        """
        # Create a unique bin name
        bin_name = self._generate_bin_name()
        bin_url = f"{self.base_url}/{bin_name}"
        file_url = f"{bin_url}/{filename}"

        headers = {
            "Content-Type": "application/octet-stream",
            "User-Agent": "twat-fs/1.0",
        }

        # Upload with retries
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                file.seek(0)  # Reset file pointer for each attempt
                response = requests.put(
                    file_url,
                    data=file,
                    headers=headers,
                    timeout=30,
                )

                # Use standardized HTTP response handling
                try:
                    handle_http_response(response, self.provider_name)
                    return file_url
                except RetryableError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise

            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                msg = f"Request failed: {e}"
                raise NonRetryableError(msg, self.provider_name) from e

        # This should never be reached due to the exception handling above
        msg = "Upload failed after retries"
        raise NonRetryableError(msg, self.provider_name) from None

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # Get the filename from the file object
            filename = Path(file.name).name

            # Upload the file
            url = self._do_upload(file, filename)

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
    return FilebinProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Return an instance of the provider"""
    return FilebinProvider.get_provider()


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
        "filebin",
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
