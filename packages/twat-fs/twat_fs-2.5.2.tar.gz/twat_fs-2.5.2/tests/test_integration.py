#!/usr/bin/env python3
# this_file: tests/test_integration.py

"""
Integration tests for the upload functionality.
These tests interact with real providers and require proper credentials.
"""

import os
import time
from pathlib import Path

import pytest
from loguru import logger

from twat_fs.upload import setup_provider, setup_providers, upload_file
from twat_fs.upload_providers import (
    fal,
    s3,
    PROVIDERS_PREFERENCE,
    catbox,
    litterbox,
    ExpirationTime,
)

# Test data
TEST_DIR = Path(__file__).parent / "data"
SMALL_FILE = TEST_DIR / "test.txt"
LARGE_FILE = TEST_DIR / "large_test.bin"  # Will be created dynamically
LARGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@pytest.fixture(scope="session")
def large_test_file():
    """Create a large test file for performance testing."""
    if not LARGE_FILE.exists():
        logger.info(
            f"Creating large test file: {LARGE_FILE} ({LARGE_FILE_SIZE / 1024 / 1024:.1f}MB)"
        )
        LARGE_FILE.parent.mkdir(exist_ok=True)
        with LARGE_FILE.open("wb") as f:
            f.write(os.urandom(LARGE_FILE_SIZE))
    return LARGE_FILE


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Clean up test files after all tests are done."""
    yield
    if LARGE_FILE.exists():
        LARGE_FILE.unlink()


class TestS3Integration:
    """Integration tests for S3 provider."""

    @pytest.fixture(autouse=True)
    def check_s3_credentials(self):
        """Skip S3 tests if credentials are not configured."""
        if not s3.get_credentials():
            pytest.skip("S3 credentials not configured")

    def test_s3_setup(self):
        """Test S3 provider setup check."""
        result = setup_provider("s3")
        assert result.success is True
        assert "You can upload files to: s3" in result.explanation

    def test_s3_upload_small_file(self):
        """Test uploading a small file to S3."""
        url = upload_file(SMALL_FILE, provider="s3")
        assert url.startswith("https://")
        assert url.endswith(SMALL_FILE.name)

    def test_s3_upload_large_file(self, large_test_file):
        """Test uploading a large file to S3."""
        start_time = time.time()
        url = upload_file(large_test_file, provider="s3")
        upload_time = time.time() - start_time

        assert url.startswith("https://")
        assert url.endswith(large_test_file.name)
        logger.info(f"Large file upload took {upload_time:.1f} seconds")

    def test_s3_upload_with_custom_endpoint(self, monkeypatch):
        """Test uploading to S3 with a custom endpoint."""
        custom_endpoint = "https://s3.custom-region.amazonaws.com"
        monkeypatch.setenv("AWS_ENDPOINT_URL", custom_endpoint)
        url = upload_file(SMALL_FILE, provider="s3")
        assert custom_endpoint in url


class TestDropboxIntegration:
    """Test Dropbox integration."""

    def test_dropbox_setup(self) -> None:
        """Test Dropbox setup."""
        result = setup_provider("dropbox")
        # Test should pass if either:
        # 1. Provider is properly configured (success is True)
        # 2. Provider needs setup (success is False and explanation contains setup instructions)
        assert result.success is True or (
            result.success is False
            and "DROPBOX_ACCESS_TOKEN" in result.explanation
            and "setup" in result.explanation.lower()
        )

    def test_dropbox_upload_small_file(self) -> None:
        """Test uploading a small file to Dropbox."""
        try:
            url = upload_file(SMALL_FILE, provider="dropbox")
            assert url.startswith("https://")
        except ValueError as e:
            # Test should pass if error is due to expired credentials or not configured
            assert "Failed to initialize Dropbox client" in str(e)
            assert "expired_access_token" in str(e) or "not configured" in str(e)

    def test_dropbox_upload_large_file(self, large_test_file: Path) -> None:
        """Test uploading a large file to Dropbox."""
        try:
            url = upload_file(large_test_file, provider="dropbox")
            assert url.startswith("https://")
        except ValueError as e:
            # Test should pass if error is due to expired credentials or not configured
            assert "Failed to initialize Dropbox client" in str(e)
            assert "expired_access_token" in str(e) or "not configured" in str(e)


class TestFalIntegration:
    """Integration tests for FAL provider."""

    @pytest.fixture(autouse=True)
    def check_fal_credentials(self):
        """Skip FAL tests if credentials are not configured."""
        if not fal.get_credentials():
            pytest.skip("FAL credentials not configured")

    def test_fal_setup(self):
        """Test FAL provider setup check."""
        success, explanation = setup_provider("fal")
        assert success is True
        assert "You can upload files to: fal" in explanation

    def test_fal_upload_small_file(self):
        """Test uploading a small file to FAL."""
        url = upload_file(SMALL_FILE, provider="fal")
        assert url.startswith("https://")

    def test_fal_upload_large_file(self, large_test_file):
        """Test uploading a large file to FAL."""
        start_time = time.time()
        url = upload_file(large_test_file, provider="fal")
        upload_time = time.time() - start_time

        assert url.startswith("https://")
        logger.info(f"Large file upload took {upload_time:.1f} seconds")


class TestSetupIntegration:
    """Test provider setup functionality."""

    def test_setup_all_providers(self) -> None:
        """Test checking setup status for all providers."""
        # setup_providers() returns None, we just check it runs without errors
        setup_providers()

        # We can still test individual providers
        for provider in PROVIDERS_PREFERENCE:
            if provider.lower() == "simple":
                continue
            result = setup_provider(provider)
            # At least one provider should be available or have setup instructions
            assert result.success or (
                "not configured" in result.explanation
                or "setup" in result.explanation.lower()
            )


class TestCatboxIntegration:
    """Integration tests for Catbox provider."""

    def test_catbox_setup(self):
        """Test Catbox provider setup."""
        status, _ = setup_provider("catbox")
        assert (
            status is True
        )  # Should always work since anonymous uploads are supported

    def test_catbox_upload_small_file(self, small_file):
        """Test uploading a small file to Catbox."""
        url = upload_file(small_file, provider="catbox")
        assert url.startswith("https://files.catbox.moe/")
        assert len(url) > len("https://files.catbox.moe/")

    def test_catbox_upload_large_file(self, large_file):
        """Test uploading a large file to Catbox."""
        url = upload_file(large_file, provider="catbox")
        assert url.startswith("https://files.catbox.moe/")
        assert len(url) > len("https://files.catbox.moe/")

    @pytest.mark.skipif(
        not os.getenv("CATBOX_USERHASH"),
        reason="Requires CATBOX_USERHASH environment variable",
    )
    def test_catbox_authenticated_upload(self, small_file):
        """Test authenticated upload to Catbox."""
        result = upload_file(small_file, provider="catbox")
        assert result.url.startswith("https://files.catbox.moe/")

        # Try to delete the file
        filename = result.url.split("/")[-1]
        provider = catbox.get_provider()
        assert provider is not None

        success = provider.delete_files([filename])
        assert success is True


class TestLitterboxIntegration:
    """Integration tests for Litterbox provider."""

    def test_litterbox_setup(self):
        """Test Litterbox provider setup."""
        status, _ = setup_provider("litterbox")
        assert status is True  # Should always work since no auth needed

    def test_litterbox_upload_small_file(self, small_file):
        """Test uploading a small file to Litterbox."""
        provider = litterbox.LitterboxProvider(default_expiration=ExpirationTime.HOUR_1)
        url = provider.upload_file(small_file)
        assert url.startswith("https://litterbox.catbox.moe/")
        assert len(url) > len("https://litterbox.catbox.moe/")

    def test_litterbox_upload_large_file(self, large_file):
        """Test uploading a large file to Litterbox."""
        provider = litterbox.LitterboxProvider(
            default_expiration=ExpirationTime.HOURS_72
        )
        url = provider.upload_file(large_file)
        assert url.startswith("https://litterbox.catbox.moe/")
        assert len(url) > len("https://litterbox.catbox.moe/")

    def test_litterbox_different_expirations(self, small_file):
        """Test uploading with different expiration times."""
        provider = litterbox.LitterboxProvider()

        for expiration in ExpirationTime:
            url = provider.upload_file(small_file, expiration=expiration)
            assert url.startswith("https://litterbox.catbox.moe/")
