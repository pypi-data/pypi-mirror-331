# this_file: src/twat_fs/upload_providers/litterbox.py

"""
Litterbox.catbox.moe file upload provider.
Supports temporary file uploads with configurable expiration times.
API documentation: https://litterbox.catbox.moe/tools.php
"""

from twat_fs.upload_providers.types import UploadResult
import os
from pathlib import Path
from typing import Any, ClassVar, cast, TypeVar, ParamSpec
from collections.abc import Callable, Awaitable
from functools import wraps
import aiohttp
from loguru import logger

from twat_fs.upload_providers.protocols import ProviderClient, Provider, ProviderHelp
from twat_fs.upload_providers.types import ExpirationTime
from twat_fs.upload_providers.core import (
    convert_to_upload_result,
    with_url_validation,
    with_timing,
    RetryableError,
    NonRetryableError,
    async_to_sync,
)

# Type variables for generic functions
T = TypeVar("T")
P = ParamSpec("P")

LITTERBOX_API_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

# Provider-specific help messages
PROVIDER_HELP: ProviderHelp = {
    "setup": """No setup required. Note: Files are deleted after 24 hours by default.
Optional: Set LITTERBOX_DEFAULT_EXPIRATION environment variable to change expiration time (1h, 12h, 24h, 72h).""",
    "deps": """No additional dependencies required.""",
}


def _ensure_coroutine(
    func: Callable[P, Awaitable[str | UploadResult]],
) -> Callable[P, Awaitable[UploadResult]]:
    """
    Ensure the function returns a Coroutine type.

    Args:
        func: The async function to wrap

    Returns:
        A wrapped function that ensures UploadResult return type
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> UploadResult:
        result = await func(*args, **kwargs)
        if isinstance(result, str):
            return convert_to_upload_result(result)
        if not isinstance(result, UploadResult):
            msg = f"Expected UploadResult or str, got {type(result)}"
            raise RuntimeError(msg)
        return result

    return wrapper


class LitterboxProvider(ProviderClient, Provider):
    """Provider for litterbox.catbox.moe temporary file uploads."""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name = "litterbox"

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
        return cls(default_expiration=expiration)

    @_ensure_coroutine
    @with_url_validation
    @with_timing
    async def async_upload_file(
        self,
        file_path: str | Path,
        remote_path: str | Path | None = None,
        *,
        unique: bool = False,
        force: bool = False,
        upload_path: str | None = None,
        **kwargs: Any,
    ) -> UploadResult:
        """
        Upload a file to litterbox.catbox.moe.

        Args:
            file_path: Path to the file to upload
            remote_path: Ignored for this provider
            unique: Ignored for this provider
            force: Ignored for this provider
            upload_path: Ignored for this provider
            **kwargs: Additional provider-specific arguments

        Returns:
            UploadResult: Upload result with URL and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        file_path = Path(str(file_path))
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        expiration = kwargs.get("expiration") or self.default_expiration
        data = aiohttp.FormData()
        data.add_field("reqtype", "fileupload")
        data.add_field(
            "time",
            str(
                expiration.value
                if isinstance(expiration, ExpirationTime)
                else expiration
            ),
        )

        try:
            # Read file content first
            with open(str(file_path), "rb") as f:
                file_content = f.read()

            # Create FormData with file content
            data.add_field(
                "fileToUpload",
                file_content,
                filename=str(file_path.name),
                content_type="application/octet-stream",
            )

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(LITTERBOX_API_URL, data=data) as response:
                        if response.status == 503:
                            msg = "Service temporarily unavailable"
                            raise RetryableError(msg, "litterbox")
                        elif response.status == 404:
                            msg = "API endpoint not found - service may be down or API has changed"
                            raise RetryableError(msg, "litterbox")
                        elif response.status != 200:
                            error_text = await response.text()
                            msg = f"Upload failed with status {response.status}: {error_text}"
                            if response.status in (400, 401, 403):
                                raise NonRetryableError(msg, "litterbox")
                            raise RetryableError(msg, "litterbox")

                        url = await response.text()
                        if not url.startswith("http"):
                            msg = f"Invalid response from server: {url}"
                            raise NonRetryableError(msg, "litterbox")

                        return convert_to_upload_result(
                            url,
                            metadata={
                                "expiration": expiration.value,
                                "provider": self.provider_name,
                            },
                        )

                except aiohttp.ClientError as e:
                    msg = f"Upload failed: {e}"
                    raise RetryableError(msg, "litterbox") from e

        except Exception as e:
            msg = f"Upload failed: {e}"
            raise RetryableError(msg, "litterbox") from e

    def upload_file(
        self,
        local_path: str | Path,
        remote_path: str | Path | None = None,
        *,
        unique: bool = False,
        force: bool = False,
        upload_path: str | None = None,
        **kwargs: Any,
    ) -> UploadResult:
        """
        Synchronously upload a file to litterbox.catbox.moe.

        Args:
            local_path: Path to the file to upload
            remote_path: Ignored for this provider
            unique: Ignored for this provider
            force: Ignored for this provider
            upload_path: Ignored for this provider
            **kwargs: Additional provider-specific arguments

        Returns:
            UploadResult: Upload result with URL and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        return cast(
            UploadResult,
            async_to_sync(self.async_upload_file)(
                local_path,
                remote_path,
                unique=unique,
                force=force,
                upload_path=upload_path,
                **kwargs,
            ),
        )


def get_credentials() -> dict[str, Any] | None:
    """Get provider credentials from environment."""
    return LitterboxProvider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Initialize and return the provider client."""
    return LitterboxProvider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    expiration: ExpirationTime | None = None,
) -> UploadResult:
    """
    Upload a file to litterbox.catbox.moe.

    Args:
        local_path: Path to the file to upload
        remote_path: Ignored for this provider
        expiration: Optional expiration time for the upload

    Returns:
        UploadResult: Upload result with URL and metadata

    Raises:
        FileNotFoundError: If the file doesn't exist
        RetryableError: For temporary failures that can be retried
        NonRetryableError: For permanent failures
    """
    provider = get_provider()
    if not provider:
        msg = "Failed to initialize Litterbox provider"
        raise NonRetryableError(msg, "litterbox")
    return provider.upload_file(local_path, remote_path, expiration=expiration)
