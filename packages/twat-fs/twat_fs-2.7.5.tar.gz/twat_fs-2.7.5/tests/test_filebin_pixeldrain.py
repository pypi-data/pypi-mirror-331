#!/usr/bin/env python
# /// script
# dependencies = ["pytest", "requests", "responses", "types-requests", "types-responses"]
# ///
# this_file: tests/test_filebin_pixeldrain.py

"""Tests for filebin.net and pixeldrain.com upload providers."""

import pytest
import responses
import re
from pathlib import Path

from twat_fs.upload_providers import filebin, pixeldrain
from twat_fs.upload_providers.types import UploadResult


@pytest.fixture
def test_file(tmp_path: Path) -> Path:
    """Create a test file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path


@responses.activate  # type: ignore[misc]
def test_filebin_upload_success(test_file: Path) -> None:
    """Test successful file upload to filebin.net."""
    # Mock the filebin.net response with regex pattern for URL
    responses.add(
        responses.PUT,  # Changed from POST to PUT to match the implementation
        re.compile(
            r"https://filebin\.net/.*"
        ),  # Use regex pattern for flexible URL matching
        status=200,
        body="",  # Filebin returns empty body
        headers={"Location": "https://filebin.net/abc123/test.txt"},
    )

    # Test the upload
    provider = filebin.FilebinProvider()
    result = provider.upload_file(test_file)
    assert isinstance(result, UploadResult)
    # Check for URL pattern rather than exact value since the bin name is generated dynamically
    assert re.match(r"https://filebin\.net/.+/test\.txt", result.url)
    assert result.metadata["provider"] == "filebin"
    assert result.metadata["success"] is True


@responses.activate  # type: ignore[misc]
def test_filebin_upload_failure(test_file: Path) -> None:
    """Test failed file upload to filebin.net."""
    # Mock the filebin.net error response
    responses.add(
        responses.PUT,  # Changed from POST to PUT
        re.compile(
            r"https://filebin\.net/.*"
        ),  # Use regex pattern for flexible URL matching
        status=500,
        json={"error": "Internal server error"},
    )

    # Test the upload
    provider = filebin.FilebinProvider()
    with pytest.raises(RuntimeError, match="Upload failed"):
        provider.upload_file(test_file)


@responses.activate  # type: ignore[misc]
def test_pixeldrain_upload_success(test_file: Path) -> None:
    """Test successful file upload to pixeldrain.com."""
    # Mock the pixeldrain.com response
    responses.add(
        responses.POST,
        "https://pixeldrain.com/api/file",
        status=200,
        json={"id": "abc123", "name": "test.txt", "size": 12},
    )

    # Test the upload
    provider = pixeldrain.PixeldrainProvider()
    result = provider.upload_file(test_file)
    assert isinstance(result, UploadResult)
    assert result.url == "https://pixeldrain.com/u/abc123"
    assert result.metadata["provider"] == "pixeldrain"
    assert result.metadata["success"] is True


@responses.activate  # type: ignore[misc]
def test_pixeldrain_upload_failure(test_file: Path) -> None:
    """Test failed file upload to pixeldrain.com."""
    # Mock the pixeldrain.com error response
    responses.add(
        responses.POST,
        "https://pixeldrain.com/api/file",
        status=500,
        json={"error": "Internal server error"},
    )

    # Test the upload
    provider = pixeldrain.PixeldrainProvider()
    with pytest.raises(RuntimeError, match="Upload failed"):
        provider.upload_file(test_file)


def test_filebin_provider_initialization() -> None:
    """Test filebin.net provider initialization."""
    provider = filebin.get_provider()
    assert provider is not None
    assert isinstance(provider, filebin.FilebinProvider)


def test_pixeldrain_provider_initialization() -> None:
    """Test pixeldrain.com provider initialization."""
    provider = pixeldrain.get_provider()
    assert provider is not None
    assert isinstance(provider, pixeldrain.PixeldrainProvider)
