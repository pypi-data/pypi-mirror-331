# this_file: src/twat_fs/upload_providers/types.py

"""
Common types used across upload providers.
"""

from enum import Enum
from typing import Any


class ExpirationTime(str, Enum):
    """Valid expiration times for Litterbox uploads."""

    HOUR_1 = "1h"
    HOURS_12 = "12h"
    HOURS_24 = "24h"
    HOURS_72 = "72h"


class UploadResult:
    """Result of an upload operation."""

    def __init__(self, url: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Initialize an upload result.

        Args:
            url: The URL where the uploaded file can be accessed
            metadata: Optional metadata about the upload
        """
        self.url = url
        self.metadata = metadata or {}
