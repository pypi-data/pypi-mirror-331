# this_file: src/twat_fs/upload_providers/litterbox.py

"""
Litterbox.catbox.moe file upload provider.
Supports temporary file uploads with configurable expiration times.
API documentation: https://litterbox.catbox.moe/tools.php
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, BinaryIO, ClassVar, cast

import aiohttp
from loguru import logger

from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.types import ExpirationTime, UploadResult
from twat_fs.upload_providers.core import (
    convert_to_upload_result,
    RetryableError,
    NonRetryableError,
    async_to_sync,
)
from twat_fs.upload_providers.utils import (
    create_provider_help,
    log_upload_attempt,
    handle_http_response,
)

LITTERBOX_API_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

# Provider-specific help messages
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="""No setup required. Note: Files are deleted after 24 hours by default.
Optional: Set LITTERBOX_DEFAULT_EXPIRATION environment variable to change expiration time (1h, 12h, 24h, 72h).""",
    dependency_info="""No additional dependencies required.""",
)


class LitterboxProvider(BaseProvider):
    """Provider for litterbox.catbox.moe temporary file uploads."""

    # Class variables
    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: ClassVar[str] = "litterbox"

    # Environment variables
    OPTIONAL_ENV_VARS: ClassVar[list[str]] = ["LITTERBOX_DEFAULT_EXPIRATION"]

    def __init__(
        self, default_expiration: ExpirationTime | str = ExpirationTime.HOURS_12
    ) -> None:
        """
        Initialize the Litterbox provider.

        Args:
            default_expiration: Default expiration time for uploads

        Raises:
            ValueError: If the expiration time is invalid
        """
        super().__init__()
        # If a string is provided, convert it to ExpirationTime
        if not isinstance(default_expiration, ExpirationTime):
            try:
                default_expiration = ExpirationTime(default_expiration)
            except Exception as e:
                msg = f"Invalid expiration time: {default_expiration}"
                raise ValueError(msg) from e
        self.default_expiration = default_expiration

    @classmethod
    def get_credentials(cls) -> dict[str, Any] | None:
        """
        Get litterbox credentials from environment.
        Currently no credentials are needed for litterbox.

        Returns:
            None: Litterbox doesn't require credentials
        """
        return None

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """
        Initialize and return the litterbox provider.

        Returns:
            ProviderClient: Configured litterbox provider
        """
        default_expiration = str(
            os.getenv("LITTERBOX_DEFAULT_EXPIRATION", "24h")
        ).strip()
        try:
            expiration = ExpirationTime(str(default_expiration))
        except ValueError:
            logger.warning(
                f"Invalid expiration time {default_expiration}, using 24h default"
            )
            expiration = ExpirationTime.HOURS_24

        provider = cls(default_expiration=expiration)
        return cast(ProviderClient, provider)

    async def _do_upload_async(
        self, file: BinaryIO, expiration: ExpirationTime | str | None = None
    ) -> str:
        """
        Internal method to handle the actual upload to litterbox.catbox.moe.

        Args:
            file: Open file handle to upload
            expiration: Expiration time for the upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        expiration_value = expiration or self.default_expiration

        data = aiohttp.FormData()
        data.add_field("reqtype", "fileupload")
        data.add_field(
            "time",
            str(
                expiration_value.value
                if isinstance(expiration_value, ExpirationTime)
                else expiration_value
            ),
        )

        try:
            # Read file content
            file_content = file.read()
            file_name = os.path.basename(file.name)

            # Create FormData with file content
            data.add_field(
                "fileToUpload",
                file_content,
                filename=file_name,
                content_type="application/octet-stream",
            )

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(LITTERBOX_API_URL, data=data) as response:
                        # Handle HTTP response status codes
                        handle_http_response(response, self.provider_name)

                        url = await response.text()
                        if not url.startswith("http"):
                            msg = f"Invalid response from server: {url}"
                            raise NonRetryableError(msg, self.provider_name)

                        return url

                except aiohttp.ClientError as e:
                    msg = f"Upload failed: {e}"
                    raise RetryableError(msg, self.provider_name) from e

        except (RetryableError, NonRetryableError):
            raise
        except Exception as e:
            msg = f"Upload failed: {e}"
            raise RetryableError(msg, self.provider_name) from e

    def _do_upload(
        self, file: BinaryIO, expiration: ExpirationTime | str | None = None
    ) -> str:
        """
        Synchronous version of _do_upload_async.

        Args:
            file: Open file handle to upload
            expiration: Expiration time for the upload

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        return async_to_sync(self._do_upload_async)(file, expiration)

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
                    "expiration": self.default_expiration.value,
                    "success": True,
                },
            )
        except Exception as e:
            log_upload_attempt(self.provider_name, file.name, success=False, error=e)
            raise

    def upload_file(
        self,
        local_path: str | Path,
        remote_path: str | Path | None = None,
        *,
        unique: bool = False,
        force: bool = False,
        upload_path: str | None = None,
        expiration: ExpirationTime | str | None = None,
        **kwargs: Any,
    ) -> UploadResult:
        """
        Upload a file to litterbox.catbox.moe.

        Args:
            local_path: Path to the file to upload
            remote_path: Ignored for this provider
            unique: Ignored for this provider
            force: Ignored for this provider
            upload_path: Ignored for this provider
            expiration: Expiration time for the upload
            **kwargs: Additional provider-specific arguments

        Returns:
            UploadResult: Upload result with URL and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        path = Path(local_path)
        self._validate_file(path)

        with self._open_file(path) as file:
            if expiration:
                # If expiration is provided, use _do_upload directly
                try:
                    url = self._do_upload(file, expiration)
                    log_upload_attempt(self.provider_name, file.name, success=True)

                    return convert_to_upload_result(
                        url,
                        metadata={
                            "provider": self.provider_name,
                            "expiration": str(expiration),
                            "success": True,
                        },
                    )
                except Exception as e:
                    log_upload_attempt(
                        self.provider_name, file.name, success=False, error=e
                    )
                    raise
            else:
                # Otherwise use the standard implementation
                return super().upload_file(
                    local_path,
                    remote_path,
                    unique=unique,
                    force=force,
                    upload_path=upload_path,
                    **kwargs,
                )


# Module-level functions that delegate to the LitterboxProvider class
def get_credentials() -> dict[str, Any] | None:
    """Get litterbox credentials from environment."""
    return LitterboxProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Initialize and return the litterbox provider."""
    return LitterboxProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
    expiration: ExpirationTime | str | None = None,
) -> UploadResult:
    """
    Upload a file to litterbox.catbox.moe.

    Args:
        local_path: Path to the file to upload
        remote_path: Ignored for this provider
        unique: Ignored for this provider
        force: Ignored for this provider
        upload_path: Ignored for this provider
        expiration: Expiration time for the upload

    Returns:
        UploadResult: Upload result with URL and metadata

    Raises:
        FileNotFoundError: If the file doesn't exist
        RetryableError: For temporary failures that can be retried
        NonRetryableError: For permanent failures
        ValueError: If provider initialization fails
    """
    provider = get_provider()
    if not provider:
        msg = "Failed to initialize litterbox provider"
        raise ValueError(msg)

    return provider.upload_file(
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
        expiration=expiration,
    )
