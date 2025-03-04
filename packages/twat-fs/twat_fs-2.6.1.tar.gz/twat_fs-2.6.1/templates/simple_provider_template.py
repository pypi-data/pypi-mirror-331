# this_file: templates/simple_provider_template.py

"""
Template for refactoring simple provider classes that don't require credentials.
Replace PROVIDER_NAME with the actual provider name.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, ClassVar, cast

# Import the appropriate HTTP library (aiohttp or requests)
import requests  # or import aiohttp

from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.utils import (
    create_provider_help,
    handle_http_response,
    log_upload_attempt,
    standard_upload_wrapper,
)

# Use standardized provider help format
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="No setup required. [Add provider-specific details here.]",
    dependency_info="[Add dependencies here, e.g. requests, aiohttp]",
)


class ProviderNameProvider(BaseProvider):
    """Provider for uploading files to provider_name."""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "provider_name"
    upload_url: str = "https://example.com/upload"  # Replace with actual URL

    @classmethod
    def get_credentials(cls) -> None:
        """No credentials needed for this provider."""
        return None

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """Get an instance of the provider."""
        return cast(ProviderClient, cls())

    # Choose one of the following implementation methods based on the provider's API:

    # Option 1: For providers with synchronous APIs
    def _do_upload(self, file_path: Path) -> str:
        """
        Internal implementation of the file upload.

        Args:
            file_path: Path to the file to upload

        Returns:
            URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting
            NonRetryableError: If the upload fails for any other reason
        """
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(
                self.upload_url,
                files=files,
                timeout=30,
            )

            # Use standardized HTTP response handling
            handle_http_response(response, self.provider_name)

            # Process response to extract URL
            url = response.text.strip()  # Modify based on provider response format
            return url

    # Option 2: For providers with asynchronous APIs
    async def _do_upload_async(self, file_path: Path) -> str:
        """
        Internal implementation of the file upload using async API.

        Args:
            file_path: Path to the file to upload

        Returns:
            URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting
            NonRetryableError: If the upload fails for any other reason
        """
        import aiohttp

        data = aiohttp.FormData()
        # Add appropriate fields based on provider requirements
        data.add_field("file", open(file_path, "rb"), filename=file_path.name)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.upload_url, data=data) as response:
                # Use standardized HTTP response handling
                handle_http_response(response, self.provider_name)

                # Process response to extract URL
                response_text = await response.text()
                # Modify based on provider response format
                return response_text.strip()

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # Choose one of the following approaches based on the implementation above:

            # For synchronous implementation:
            temp_path = Path(file.name)
            url = self._do_upload(temp_path)

            # For asynchronous implementation:
            # temp_path = Path(file.name)
            # url = asyncio.run(self._do_upload_async(temp_path))

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


# Module-level functions to implement the Provider protocol
def get_credentials() -> None:
    """No credentials needed for this provider."""
    return ProviderNameProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Get an instance of the provider."""
    return ProviderNameProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
) -> UploadResult:
    """
    Upload a file to the provider.

    Args:
        local_path: Path to the file to upload
        remote_path: Ignored for this provider
        unique: Ignored for this provider
        force: Ignored for this provider
        upload_path: Ignored for this provider

    Returns:
        UploadResult with the URL of the uploaded file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a file
        PermissionError: If the file can't be read
        RuntimeError: If the upload fails
    """
    return standard_upload_wrapper(
        get_provider(),
        "provider_name",  # Replace with actual provider name
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
