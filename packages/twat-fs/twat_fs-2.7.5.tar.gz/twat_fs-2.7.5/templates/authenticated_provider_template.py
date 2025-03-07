# this_file: templates/authenticated_provider_template.py

"""
Template for refactoring providers that require credentials.
Replace PROVIDER_NAME with the actual provider name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, ClassVar, cast

# Import the appropriate HTTP library and provider-specific libraries
import requests  # or import aiohttp

from twat_fs.upload_providers.protocols import ProviderClient, ProviderHelp
from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.core import NonRetryableError
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.utils import (
    create_provider_help,
    get_env_credentials,
    handle_http_response,
    log_upload_attempt,
    standard_upload_wrapper,
)

# Use standardized provider help format
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="Requires environment variables: [LIST_REQUIRED_ENV_VARS]. [Add provider-specific setup details here.]",
    dependency_info="[Add dependencies here, e.g. provider-specific SDK]",
)


class ProviderNameProvider(BaseProvider):
    """Provider for uploading files to provider_name."""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: str = "provider_name"

    # Required environment variables
    REQUIRED_ENV_VARS = [
        "PROVIDER_API_KEY",  # Replace with actual env var names
        "PROVIDER_API_SECRET",
    ]

    # Optional environment variables
    OPTIONAL_ENV_VARS = [
        "PROVIDER_REGION",  # Replace with actual env var names
        "PROVIDER_OPTIONS",
    ]

    def __init__(self, credentials: dict[str, str]) -> None:
        """
        Initialize the provider with credentials.

        Args:
            credentials: Dictionary of credentials from environment variables
        """
        self.provider_name = "provider_name"
        self.api_key = credentials.get("PROVIDER_API_KEY")
        self.api_secret = credentials.get("PROVIDER_API_SECRET")
        self.region = credentials.get("PROVIDER_REGION", "default_region")

        # Initialize the provider-specific client
        # Example:
        # self.client = ProviderSDK(
        #     api_key=self.api_key,
        #     api_secret=self.api_secret,
        #     region=self.region,
        # )

    @classmethod
    def get_credentials(cls) -> dict[str, str] | None:
        """
        Get credentials from environment variables.

        Returns:
            Dictionary of credentials or None if required variables are missing
        """
        return get_env_credentials(
            required_vars=cls.REQUIRED_ENV_VARS,
            optional_vars=cls.OPTIONAL_ENV_VARS,
        )

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """
        Initialize and return the provider client.

        Returns:
            ProviderClient instance or None if credentials are missing
        """
        credentials = cls.get_credentials()
        if not credentials:
            return None

        try:
            return cast(ProviderClient, cls(credentials))
        except Exception as e:
            from loguru import logger

            logger.error(f"Failed to initialize {cls.provider_name} provider: {e}")
            return None

    def _do_upload(self, file_path: Path, remote_path: Path | None = None) -> str:
        """
        Internal implementation of the file upload.

        Args:
            file_path: Path to the file to upload
            remote_path: Optional remote path for the file

        Returns:
            URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to rate limiting
            NonRetryableError: If the upload fails for any other reason
        """
        # Implement provider-specific upload logic
        # Example using provider SDK:
        # result = self.client.upload_file(
        #     file_path=str(file_path),
        #     destination=str(remote_path) if remote_path else None,
        # )
        # return result.get_url()

        # Example using HTTP:
        with open(file_path, "rb") as f:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/octet-stream",
            }

            dest_path = remote_path.name if remote_path else file_path.name

            response = requests.post(
                f"https://api.provider.com/upload?path={dest_path}",
                headers=headers,
                data=f,
                timeout=60,
            )

            handle_http_response(response, self.provider_name)

            # Process response to extract URL
            data = response.json()
            url = data.get("url", "")
            if not url:
                msg = "No URL found in response"
                raise NonRetryableError(msg, self.provider_name)
            return str(url)

    def upload_file_impl(
        self, file: BinaryIO, remote_path: Path | None = None
    ) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload
            remote_path: Optional remote path for the file

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # For authenticated providers, we often need to handle remote paths
            temp_path = Path(file.name)
            url = self._do_upload(temp_path, remote_path)

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
                    "remote_path": str(remote_path) if remote_path else None,
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

    # Override the BaseProvider's upload_file method to handle remote paths
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
        Upload a file to the provider.

        Args:
            local_path: Path to the file to upload
            remote_path: Optional remote path for the file
            unique: If True, ensures unique filename
            force: If True, overwrites existing file
            upload_path: Custom upload path
            **kwargs: Additional provider-specific arguments

        Returns:
            UploadResult with the URL of the uploaded file

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is not a file
            PermissionError: If the file can't be read
            RuntimeError: If the upload fails
        """
        path = Path(local_path)
        self._validate_file(path)

        # Process remote_path if provided
        remote = None
        if remote_path:
            remote = Path(str(remote_path))
        elif upload_path:
            remote = Path(upload_path) / path.name

        # Add unique suffix if requested
        if unique and remote:
            import uuid

            suffix = uuid.uuid4().hex[:8]
            remote = remote.with_stem(f"{remote.stem}_{suffix}")

        with self._open_file(path) as file:
            result = self.upload_file_impl(file, remote)
            if not result.metadata.get("success", True):
                msg = f"Upload failed: {result.metadata.get('error', 'Unknown error')}"
                raise RuntimeError(msg)
            return result


# Module-level functions to implement the Provider protocol
def get_credentials() -> dict[str, str] | None:
    """Get credentials for the provider."""
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
        remote_path: Optional remote path for the file
        unique: If True, ensures unique filename
        force: If True, overwrites existing file
        upload_path: Custom upload path

    Returns:
        UploadResult with the URL of the uploaded file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the path is not a file or credentials are missing
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
