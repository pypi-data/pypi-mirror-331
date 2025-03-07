# this_file: src/twat_fs/upload_providers/s3.py

"""
AWS S3 provider for file uploads.
This module provides functionality to upload files to Amazon S3 storage service.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO, ClassVar, cast, TYPE_CHECKING

import boto3
from botocore.config import Config
from loguru import logger

from twat_fs.upload_providers.types import UploadResult
from twat_fs.upload_providers.core import RetryableError, NonRetryableError
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.protocols import ProviderHelp, ProviderClient
from twat_fs.upload_providers.utils import (
    create_provider_help,
    get_env_credentials,
    log_upload_attempt,
    standard_upload_wrapper,
)

if TYPE_CHECKING:
    from twat_fs.upload_providers.types import UploadResult

# Use standardized provider help format
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="""To use AWS S3 storage:
1. Create an AWS account if you don't have one
2. Create an S3 bucket to store your files
3. Set up AWS credentials by either:
   - Creating an IAM user and setting AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - Using AWS CLI: run 'aws configure'
   - Setting up IAM roles if running on AWS infrastructure
4. Set the following environment variables:
   - AWS_S3_BUCKET: Name of your S3 bucket
   - AWS_DEFAULT_REGION: AWS region (e.g. us-east-1)
   Optional:
   - AWS_ENDPOINT_URL: Custom S3 endpoint
   - AWS_S3_PATH_STYLE: Set to 'true' for path-style endpoints
   - AWS_ROLE_ARN: ARN of role to assume""",
    dependency_info="""Additional setup needed:
1. Install the AWS SDK: pip install boto3
2. If using AWS CLI: pip install awscli
3. Configure AWS credentials using one of the methods above
4. Ensure your IAM user/role has necessary S3 permissions:
   - s3:PutObject
   - s3:GetObject
   - s3:ListBucket""",
)


class S3Provider(BaseProvider):
    """Provider for AWS S3 uploads"""

    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name: ClassVar[str] = "s3"

    # Required environment variables
    REQUIRED_ENV_VARS: ClassVar[list[str]] = [
        "AWS_S3_BUCKET",
    ]

    # Optional environment variables
    OPTIONAL_ENV_VARS: ClassVar[list[str]] = [
        "AWS_DEFAULT_REGION",
        "AWS_ENDPOINT_URL",
        "AWS_S3_PATH_STYLE",
        "AWS_ROLE_ARN",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
    ]

    def __init__(self, credentials: dict[str, Any]) -> None:
        """
        Initialize the S3 provider with credentials.

        Args:
            credentials: Dictionary containing S3 credentials and configuration
        """
        self.provider_name = "s3"
        self.credentials = credentials
        self.client = self._create_client()

    def _create_client(self) -> Any:
        """
        Create and return an S3 client using boto3.

        Returns:
            boto3.client: Configured S3 client

        Raises:
            NonRetryableError: If client creation fails
        """
        client_kwargs = {}
        if self.credentials.get("AWS_DEFAULT_REGION"):
            client_kwargs["region_name"] = self.credentials["AWS_DEFAULT_REGION"]
        if self.credentials.get("AWS_ENDPOINT_URL"):
            client_kwargs["endpoint_url"] = self.credentials["AWS_ENDPOINT_URL"]
        if self.credentials.get("AWS_S3_PATH_STYLE", "").lower() == "true":
            client_kwargs["config"] = Config(s3={"addressing_style": "path"})

        # Add credentials if provided
        if self.credentials.get("AWS_ACCESS_KEY_ID"):
            client_kwargs["aws_access_key_id"] = self.credentials["AWS_ACCESS_KEY_ID"]
        if self.credentials.get("AWS_SECRET_ACCESS_KEY"):
            client_kwargs["aws_secret_access_key"] = self.credentials[
                "AWS_SECRET_ACCESS_KEY"
            ]
        if self.credentials.get("AWS_SESSION_TOKEN"):
            client_kwargs["aws_session_token"] = self.credentials["AWS_SESSION_TOKEN"]

        try:
            return boto3.client("s3", **client_kwargs)
        except Exception as e:
            msg = f"Failed to create S3 client: {e}"
            raise NonRetryableError(msg, self.provider_name) from e

    def _get_s3_url(self, key: str) -> str:
        """
        Generate the URL for an uploaded file.

        Args:
            key: S3 object key

        Returns:
            str: URL to the uploaded file
        """
        bucket = self.credentials["AWS_S3_BUCKET"]
        if endpoint_url := self.credentials.get("AWS_ENDPOINT_URL"):
            return f"{endpoint_url}/{bucket}/{key}"
        else:
            region = self.credentials.get("AWS_DEFAULT_REGION", "us-east-1")
            return f"https://s3.{region}.amazonaws.com/{bucket}/{key}"

    def _do_upload(self, file: BinaryIO, key: str) -> str:
        """
        Internal implementation of the file upload to S3.

        Args:
            file: Open file handle to upload
            key: S3 object key

        Returns:
            str: URL of the uploaded file

        Raises:
            RetryableError: If the upload fails due to temporary issues
            NonRetryableError: If the upload fails for any other reason
        """
        bucket = self.credentials["AWS_S3_BUCKET"]

        try:
            # Reset file pointer to beginning
            file.seek(0)

            # Upload the file
            self.client.upload_fileobj(file, bucket, key)

            # Return the URL
            return self._get_s3_url(key)
        except Exception as e:
            # Handle different types of errors
            error_str = str(e)
            if "ConnectionError" in error_str or "Timeout" in error_str:
                msg = f"Temporary connection issue: {e}"
                raise RetryableError(msg, self.provider_name) from e
            else:
                msg = f"Upload failed: {e}"
                raise NonRetryableError(msg, self.provider_name) from e

    def upload_file_impl(
        self,
        file: BinaryIO,
        remote_path: str | Path | None = None,
        **kwargs: Any,
    ) -> UploadResult:
        """
        Implement the actual file upload logic.

        Args:
            file: Open file handle to upload
            remote_path: Optional remote path/key to use in S3
            **kwargs: Additional arguments

        Returns:
            UploadResult containing the URL and status
        """
        try:
            # Use original filename if no remote path specified
            key = str(remote_path or Path(file.name).name)

            # Upload the file
            url = self._do_upload(file, key)

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
                    "bucket": self.credentials["AWS_S3_BUCKET"],
                    "key": key,
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
    def get_credentials(cls) -> dict[str, Any] | None:
        """
        Get S3 credentials from environment variables.

        Returns:
            Optional[Dict[str, Any]]: Credentials dictionary or None if required vars missing
        """
        # Use get_env_credentials utility
        creds = get_env_credentials(cls.REQUIRED_ENV_VARS, cls.OPTIONAL_ENV_VARS)
        if not creds:
            return None

        return creds

    @classmethod
    def get_provider(cls) -> ProviderClient | None:
        """
        Initialize and return an S3 provider if credentials are available.

        Returns:
            Optional[ProviderClient]: Provider instance or None if initialization fails
        """
        try:
            credentials = cls.get_credentials()
            if not credentials:
                return None

            provider = cls(credentials)

            # Test the client by listing buckets
            try:
                provider.client.list_buckets()
                return cast(ProviderClient, provider)
            except Exception as e:
                logger.warning(f"Failed to validate S3 client: {e}")
                return None

        except Exception as e:
            logger.error(f"Error initializing S3 provider: {e}")
            return None


# Module-level functions to implement the Provider protocol
def get_credentials() -> dict[str, Any] | None:
    """Get S3 credentials from environment variables."""
    return S3Provider.get_credentials()


def get_provider() -> ProviderClient | None:
    """Initialize and return an S3 provider if credentials are available."""
    return S3Provider.get_provider()


def upload_file(
    local_path: str | Path,
    remote_path: str | Path | None = None,
    *,
    unique: bool = False,
    force: bool = False,
    upload_path: str | None = None,
    **kwargs: Any,
) -> UploadResult:
    """
    Upload a file to AWS S3 and return its URL.

    Args:
        local_path: Path to the file to upload
        remote_path: Optional remote path/key to use in S3
        unique: Whether to ensure unique filenames (ignored for S3)
        force: Whether to overwrite existing files (ignored for S3)
        upload_path: Custom base upload path (ignored for S3)
        **kwargs: Additional arguments

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
        "s3",
        local_path,
        remote_path,
        unique=unique,
        force=force,
        upload_path=upload_path,
        **kwargs,
    )
