# this_file: src/twat_fs/upload_providers/bashupload.py

"""
Bashupload.com upload provider.
A simple provider that uploads files to bashupload.com.
Files are automatically deleted after 3 days.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, ClassVar, cast

import aiohttp
import asyncio

from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.core import NonRetryableError
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.utils import (
    create_provider_help,
    handle_http_response,
    log_upload_attempt,
    standard_upload_wrapper,
)

# Use standardized provider help format
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="No setup required. Files are deleted after 3 days.",
    dependency_info="requests, aiohttp",
)


class BashUploadProvider(BaseProvider):
    """Provider for bashupload.com uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "bashupload"
    upload_url: str = "https://bashupload.com"

    @classmethod
    def get_credentials(cls) -> None:
        """No credentials needed for this provider."""
        return None

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """Get an instance of the provider."""
        return cast(ProviderClient, cls())

    async def _do_upload(self, file_path: Path) -> str:
        """
        Internal implementation of the file upload to bashupload.com.

        Args:
            file_path: Path to the file to upload

        Returns:
            URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting
            NonRetryableError: If the upload fails for any other reason
        """
        data = aiohttp.FormData()

        with open(file_path, "rb") as f:
            data.add_field("file", f, filename=file_path.name)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.upload_url,
                    data=data,
                    timeout=None,
                ) as response:
                    # Use standardized HTTP response handling
                    handle_http_response(response, self.provider_name)

                    response_text = await response.text()
                    for line in response_text.splitlines():
                        if line.startswith("wget "):
                            url = line.split(" ")[1].strip()
                            return f"{url}?download=1"

                    msg = f"Could not find URL in response: {response_text}"
                    raise NonRetryableError(msg, self.provider_name)

    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # We need to use a temporary path approach since BashUpload requires a file path
            # rather than a file handle for the upload
            temp_path = Path(file.name)

            # Run the async upload function
            url = asyncio.run(self._do_upload(temp_path))

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
    return BashUploadProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Get an instance of the provider."""
    return BashUploadProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
) -> UploadResult:
    """
    Upload a file to bashupload.com.

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
        "bashupload",
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
    )
