# this_file: src/twat_fs/upload_providers/pixeldrain.py

"""
Pixeldrain.com upload provider.
A simple provider that uploads files to pixeldrain.com.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import BinaryIO, cast, ClassVar

import requests

from twat_fs.upload_providers.core import (
    RetryableError,
)
from twat_fs.upload_providers.protocols import ProviderClient
from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.utils import (
    handle_http_response,
    log_upload_attempt,
)

from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.protocols import ProviderHelp
from twat_fs.upload_providers.utils import (
    create_provider_help,
    standard_upload_wrapper,
)

# Provider help messages using the standardized helper
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="No setup required.",
    dependency_info="Python package: requests",
)


class PixeldrainProvider(BaseProvider):
    """Provider for pixeldrain.com uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "pixeldrain"

    def __init__(self) -> None:
        """Initialize the Pixeldrain provider."""
        self.provider_name = "pixeldrain"
        self.url = "https://pixeldrain.com/api/file"

    def _process_response(self, response: requests.Response) -> str:
        """
        Process the HTTP response from Pixeldrain.

        Args:
            response: The HTTP response from the API

        Returns:
            str: The URL to the uploaded file

        Raises:
            ValueError: If the response is invalid
        """
        # Use the standardized HTTP response handler
        handle_http_response(response, self.provider_name)

        # Parse response JSON to get file ID
        try:
            data = response.json()
        except ValueError as e:
            msg = f"Invalid JSON response: {e}"
            raise ValueError(msg) from e

        if not data or "id" not in data:
            msg = f"Invalid response from pixeldrain: {data}"
            raise ValueError(msg)

        # Construct public URL
        return f"https://pixeldrain.com/u/{data['id']}"

    def _upload_with_retry(self, file: BinaryIO) -> str:
        """
        Upload a file with retry mechanism.

        Args:
            file: Open file handle to upload

        Returns:
            str: URL to the uploaded file

        Raises:
            ValueError: If the upload fails
            RetryableError: For temporary failures
            requests.RequestException: For network errors
        """
        # Implement retry logic manually
        max_retries = 3
        retry_delay = 2.0
        last_error = None

        for attempt in range(max_retries):
            try:
                # Reset file pointer before each attempt
                file.seek(0)

                # Prepare the upload request
                files = {"file": (file.name, file)}
                headers = {"User-Agent": "twat-fs/1.0"}

                # Send the request
                response = requests.post(
                    self.url,
                    files=files,
                    headers=headers,
                    timeout=30,
                )

                # Process the response
                return self._process_response(response)

            except (RetryableError, ValueError, requests.RequestException) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Calculate next delay (exponential backoff)
                    delay = min(retry_delay * (2**attempt), 30.0)
                    time.sleep(delay)
                else:
                    # Last attempt failed, re-raise the exception
                    if isinstance(e, RetryableError | requests.RequestException):
                        msg = f"Upload failed after {max_retries} attempts: {e}"
                        raise ValueError(msg) from e
                    raise

        # This should never be reached, but just in case
        if last_error is None:
            msg = f"Upload failed after {max_retries} attempts"
            raise ValueError(msg)
        raise ValueError(str(last_error)) from last_error

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # Upload the file with retry mechanism
            url = self._upload_with_retry(file)

            # Log success
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
                    "raw_response": {"id": url.split("/")[-1]},
                },
            )

        except Exception as e:
            # Log failure
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

    def _get_file_url(self, file_id: str | None) -> str | None:
        """Get the URL for a file ID."""
        if not file_id:
            return None
        return f"https://pixeldrain.com/u/{file_id}"


# Module-level functions to implement the Provider protocol
def get_credentials() -> None:
    """Simple providers don't need credentials"""
    return PixeldrainProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Return an instance of the provider"""
    return PixeldrainProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
) -> UploadResult:
    """
    Upload a file and return its URL.

    Args:
        local_path: Path to the file to upload
        remote_path: Optional remote path (ignored for simple providers)

    Returns:
        UploadResult: Result containing URL and metadata

    Raises:
        ValueError: If upload fails
    """
    return standard_upload_wrapper(
        get_provider(),
        "pixeldrain",
        local_path,
        remote_path,
    )
