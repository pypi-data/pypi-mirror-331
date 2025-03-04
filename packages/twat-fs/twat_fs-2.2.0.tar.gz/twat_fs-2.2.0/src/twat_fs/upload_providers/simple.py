# this_file: src/twat_fs/upload_providers/simple.py

"""
Base provider implementation with common functionality.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    Protocol,
    runtime_checkable,
    BinaryIO,
    ClassVar,
    TypeVar,
    TYPE_CHECKING,
)

from twat_fs.upload_providers.protocols import ProviderHelp, Provider, ProviderClient
from twat_fs.upload_providers.core import (
    convert_to_upload_result,
    with_url_validation,
    with_timing,
)

if TYPE_CHECKING:
    from twat_fs.upload_providers.types import UploadResult
    from collections.abc import Awaitable
    from collections.abc import Generator


@runtime_checkable
class SimpleProviderClient(Protocol):
    """Protocol for simple upload providers that just take a file and return a URL"""

    async def upload_file(self, file_path: Path) -> UploadResult:
        """Upload a file and return the result

        Args:
            file_path: Path to the file to upload

        Returns:
            UploadResult containing the URL and status
        """
        ...


T = TypeVar("T", bound="BaseProvider")


class BaseProvider(ABC, Provider):
    """Base class for all upload providers with standardized upload methods."""

    # Class variable for provider help
    PROVIDER_HELP: ClassVar[ProviderHelp] = {
        "setup": "No setup required",
        "deps": "No additional dependencies required",
    }

    @classmethod
    def get_credentials(cls) -> dict[str, Any] | None:
        """Simple providers don't need credentials by default."""
        return None

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """Initialize and return the provider client."""
        return cls()

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
        Upload a file and return its URL.
        Implements the ProviderClient interface by wrapping the async upload_file method.

        Args:
            local_path: Path to the file to upload
            remote_path: Optional remote path to use (ignored for simple providers)
            unique: If True, ensures unique filename (ignored for simple providers)
            force: If True, overwrites existing file (ignored for simple providers)
            upload_path: Custom upload path (ignored for simple providers)
            **kwargs: Additional keyword arguments

        Returns:
            UploadResult: Upload result with URL and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is not a file
            PermissionError: If the file can't be read
            RuntimeError: If the upload fails
        """
        path = Path(local_path)
        self._validate_file(path)

        with self._open_file(path) as file:
            result = self.upload_file_impl(file)
            if not result.metadata.get("success", True):
                msg = f"Upload failed: {result.metadata.get('error', 'Unknown error')}"
                raise RuntimeError(msg)
            return convert_to_upload_result(
                result.url, provider=self.provider_name, metadata=result.metadata
            )

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
    ) -> Awaitable[UploadResult]:
        """
        Upload a file using this provider.

        Args:
            file_path: Path to the file to upload
            remote_path: Optional remote path to use
            unique: If True, ensures unique filename
            force: If True, overwrites existing file
            upload_path: Custom upload path
            **kwargs: Additional provider-specific arguments

        Returns:
            Awaitable[UploadResult]: Upload result with URL and timing metrics

        Raises:
            FileNotFoundError: If the file doesn't exist
            RetryableError: For temporary failures that can be retried
            NonRetryableError: For permanent failures
        """
        # Validate file exists
        path = Path(str(file_path))
        if not path.exists():
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)

        # Return a simple URL
        return convert_to_upload_result(
            f"file://{path.absolute()}",
            metadata={
                "provider": self.provider_name,
                "local_path": str(path),
            },
        )

    @contextmanager
    def _open_file(self, file_path: Path) -> Generator[BinaryIO]:
        """Safely open and close a file"""
        file = None
        try:
            file = open(file_path, "rb")
            yield file
        finally:
            if file:
                file.close()

    def _validate_file(self, file_path: Path) -> None:
        """Validate that a file exists and is readable"""
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)
        if not file_path.is_file():
            msg = f"Not a file: {file_path}"
            raise ValueError(msg)
        if not os.access(file_path, os.R_OK):
            msg = f"Cannot read file: {file_path}"
            raise PermissionError(msg)

    @abstractmethod
    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """
        Implement the actual file upload logic.
        This method should be implemented by concrete provider classes.

        Args:
            file: Open file handle to upload

        Returns:
            UploadResult containing the URL and status
        """
        ...
