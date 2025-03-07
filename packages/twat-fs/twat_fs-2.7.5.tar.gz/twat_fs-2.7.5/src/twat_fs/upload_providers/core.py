# this_file: src/twat_fs/upload_providers/core.py

"""
Core utilities and decorators for upload providers.
Provides common functionality for retrying uploads, handling errors, and managing async operations.
"""

import asyncio
import functools
import time
from enum import Enum
from pathlib import Path
from typing import (
    TypeVar,
    ParamSpec,
    NamedTuple,
    Any,
    overload,
    Protocol,
)
from collections.abc import Callable, Awaitable
import aiohttp
from loguru import logger

from twat_cache import ucache

from twat_fs.upload_providers.types import UploadResult

# Type variables for generic decorators
T_co = TypeVar("T_co", covariant=True)
R_co = TypeVar("R_co", str, UploadResult, covariant=True)
P = ParamSpec("P")

# Constants for URL validation
URL_CHECK_TIMEOUT = aiohttp.ClientTimeout(total=30.0)  # seconds
MAX_REDIRECTS = 5
USER_AGENT = "twat-fs/1.0"


class UploadCallable(Protocol[P, T_co]):
    """Protocol for upload functions."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co: ...


class AsyncUploadCallable(Protocol[P, T_co]):
    """Protocol for async upload functions."""

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T_co: ...


@overload
def convert_to_upload_result(result: str) -> UploadResult: ...


@overload
def convert_to_upload_result(
    result: str, *, metadata: dict[str, Any]
) -> UploadResult: ...


@overload
def convert_to_upload_result(
    result: str, *, provider: str, metadata: dict[str, Any]
) -> UploadResult: ...


@overload
def convert_to_upload_result(result: UploadResult) -> UploadResult: ...


@overload
def convert_to_upload_result(result: dict[str, Any]) -> UploadResult: ...


def convert_to_upload_result(
    result: str | UploadResult | dict[str, Any],
    *,
    provider: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> UploadResult:
    """Convert various result types to UploadResult."""
    if isinstance(result, UploadResult):
        if metadata:
            result.metadata.update(metadata)
        return result
    if isinstance(result, str):
        meta = metadata or {}
        if provider:
            meta["provider"] = provider
        return UploadResult(url=result, metadata=meta)
    if isinstance(result, dict):
        return UploadResult(**result)
    msg = f"Cannot convert {type(result)} to UploadResult"
    raise TypeError(msg)


class TimingMetrics(NamedTuple):
    """Timing metrics for upload operations."""

    start_time: float
    end_time: float
    total_duration: float
    read_duration: float
    upload_duration: float
    validation_duration: float
    provider: str

    @property
    def as_dict(self) -> dict[str, float | str]:
        """Convert timing metrics to a dictionary."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
            "read_duration": self.read_duration,
            "upload_duration": self.upload_duration,
            "validation_duration": self.validation_duration,
            "provider": self.provider,
        }


class RetryStrategy(str, Enum):
    """Retry strategies for upload attempts."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[UploadCallable[P, T_co]], UploadCallable[P, T_co]]:
    """
    Decorator for retrying upload operations with configurable backoff.
    """

    def decorator(func: UploadCallable[P, T_co]) -> UploadCallable[P, T_co]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
            last_exception = None
            delay = initial_delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    # Calculate next delay based on strategy
                    if strategy == RetryStrategy.EXPONENTIAL:
                        delay = min(initial_delay * (2**attempt), max_delay)
                    elif strategy == RetryStrategy.LINEAR:
                        delay = min(initial_delay * (attempt + 1), max_delay)
                    else:  # CONSTANT
                        delay = initial_delay

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)

            assert last_exception is not None  # for type checker
            raise last_exception

        return wrapper

    return decorator


def with_async_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[AsyncUploadCallable[P, T_co]], AsyncUploadCallable[P, T_co]]:
    """
    Decorator for retrying async upload operations with configurable backoff.
    """

    def decorator(func: AsyncUploadCallable[P, T_co]) -> AsyncUploadCallable[P, T_co]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
            last_exception = None
            delay = initial_delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise

                    if strategy == RetryStrategy.EXPONENTIAL:
                        delay = min(initial_delay * (2**attempt), max_delay)
                    elif strategy == RetryStrategy.LINEAR:
                        delay = min(initial_delay * (attempt + 1), max_delay)
                    else:  # CONSTANT
                        delay = initial_delay

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)

            assert last_exception is not None  # for type checker
            raise last_exception

        return wrapper

    return decorator


def validate_file(func: UploadCallable[P, T_co]) -> UploadCallable[P, T_co]:
    """
    Decorator to validate file existence and permissions before upload.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
        # Extract file path from args or kwargs
        file_path = next(
            (arg for arg in args if isinstance(arg, str | Path)),
            kwargs.get("local_path") or kwargs.get("file_path"),
        )

        if not file_path:
            msg = "No file path provided"
            raise ValueError(msg)

        path = Path(str(file_path))  # Explicitly convert to string
        if not path.exists():
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)
        if not path.is_file():
            msg = f"Not a file: {path}"
            raise ValueError(msg)
        if not path.stat().st_size:
            msg = f"Empty file: {path}"
            raise ValueError(msg)

        return func(*args, **kwargs)

    return wrapper


def sync_to_async(func: UploadCallable[P, T_co]) -> AsyncUploadCallable[P, T_co]:
    """
    Convert a synchronous upload function to an async one.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def async_to_sync(func: AsyncUploadCallable[P, T_co]) -> UploadCallable[P, T_co]:
    """
    Convert an async upload function to a synchronous one.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


class UploadError(Exception):
    """Base class for upload errors."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        """Initialize with message and optional provider name."""
        super().__init__(message)
        self.provider = provider


class RetryableError(UploadError):
    """Error that can be retried (e.g., network issues)."""


class NonRetryableError(UploadError):
    """Error that should not be retried (e.g., invalid credentials)."""


@ucache(ttl=86400)  # Cache for 24 hours
async def validate_url(
    url: str, timeout: aiohttp.ClientTimeout = URL_CHECK_TIMEOUT
) -> bool:
    """
    Validate that a URL is accessible.

    Args:
        url: URL to validate
        timeout: Request timeout

    Returns:
        bool: True if URL is accessible, False otherwise

    Raises:
        RetryableError: If validation fails due to temporary issues
        NonRetryableError: If validation fails due to permanent issues
    """
    try:
        async with (
            aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": USER_AGENT},
            ) as session,
            session.head(
                url,
                allow_redirects=True,
                max_redirects=MAX_REDIRECTS,
            ) as response,
        ):
            if response.status in (200, 201, 202, 203, 204):
                return True
            if response.status in (401, 403, 404):
                msg = f"URL validation failed with status {response.status}"
                raise NonRetryableError(msg)
            msg = f"URL validation failed with status {response.status}"
            raise RetryableError(msg)
    except aiohttp.ClientError as e:
        msg = f"URL validation failed: {e}"
        raise RetryableError(msg) from e


@with_async_retry(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    strategy=RetryStrategy.EXPONENTIAL,
    exceptions=(RetryableError, aiohttp.ClientError),
)
async def ensure_url_accessible(url: str) -> UploadResult:
    """
    Ensure a URL is accessible, with retries.

    Args:
        url: URL to validate

    Returns:
        UploadResult: Upload result with validated URL

    Raises:
        RetryableError: If validation fails after retries
        NonRetryableError: If validation fails permanently
    """
    if await validate_url(url):
        return convert_to_upload_result(url)
    msg = "URL validation failed"
    raise RetryableError(msg)


def with_url_validation(
    func: Callable[P, Awaitable[str | UploadResult]],
) -> Callable[P, Awaitable[UploadResult]]:
    """
    Decorator to validate URLs after upload.

    Args:
        func: Async function that returns a URL or UploadResult

    Returns:
        Callable: Wrapped function that ensures URL is accessible
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> UploadResult:
        result = await func(*args, **kwargs)
        if isinstance(result, str):
            return await ensure_url_accessible(result)
        return result

    return wrapper


def with_timing(func: Callable[P, Awaitable[T_co]]) -> Callable[P, Awaitable[T_co]]:
    """
    Decorator to add timing metrics to upload results.

    Args:
        func: Async function to time

    Returns:
        Callable: Wrapped function that includes timing metrics
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_co:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()

        if isinstance(result, UploadResult):
            result.metadata["timing"] = {
                "start_time": start_time,
                "end_time": end_time,
                "total_duration": end_time - start_time,
            }

        return result

    return wrapper
