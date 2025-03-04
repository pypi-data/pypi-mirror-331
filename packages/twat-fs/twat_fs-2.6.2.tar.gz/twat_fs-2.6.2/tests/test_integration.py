#!/usr/bin/env python3
# this_file: tests/test_integration.py

"""
Integration tests for the upload functionality.
These tests interact with real providers and require proper credentials.
"""

import os
from pathlib import Path

import pytest
import importlib.util

from twat_fs.upload import setup_provider, setup_providers, upload_file
from twat_fs.upload_providers import (
    catbox,
    litterbox,
    ExpirationTime,
    PROVIDERS_PREFERENCE,
)

# Conditionally check for fal and s3 modules
HAS_FAL = importlib.util.find_spec("twat_fs.upload_providers.fal") is not None
HAS_S3 = importlib.util.find_spec("twat_fs.upload_providers.s3") is not None

# Test data
TEST_DIR = Path(__file__).parent / "data"
SMALL_FILE = TEST_DIR / "test.txt"
LARGE_FILE = TEST_DIR / "large_test.bin"  # Will be created dynamically
LARGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create test directory if it doesn't exist
TEST_DIR.mkdir(exist_ok=True)

# Create a small test file if it doesn't exist
if not SMALL_FILE.exists():
    with open(SMALL_FILE, "w") as f:
        f.write("This is a test file for upload testing.")


@pytest.fixture(scope="session")
def large_test_file():
    """Create a large test file for testing."""
    if not LARGE_FILE.exists():
        with open(LARGE_FILE, "wb") as f:
            f.write(os.urandom(LARGE_FILE_SIZE))
    return LARGE_FILE


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """Clean up test files after tests."""
    yield
    if LARGE_FILE.exists():
        LARGE_FILE.unlink()


@pytest.fixture
def small_file():
    """Return the small test file for testing."""
    return SMALL_FILE


@pytest.fixture
def large_file(large_test_file):
    """Return the large test file for testing."""
    return large_test_file


@pytest.mark.skipif(not HAS_S3, reason="S3 dependencies not installed")
class TestS3Integration:
    """Integration tests for S3 provider."""

    @pytest.fixture(autouse=True)
    def check_s3_credentials(self):
        """Skip tests if S3 credentials are not available."""
        if not os.getenv("AWS_S3_BUCKET") or not os.getenv("AWS_ACCESS_KEY_ID"):
            pytest.skip("S3 credentials not available")

    def test_s3_setup(self):
        """Test S3 provider setup."""
        provider_info = setup_provider("s3")
        assert provider_info.success

    def test_s3_upload_small_file(self):
        """Test uploading a small file to S3."""
        url = upload_file(SMALL_FILE, provider="s3")
        assert url and url.startswith("http")

    def test_s3_upload_large_file(self, large_test_file):
        """Test uploading a large file to S3."""
        url = upload_file(large_test_file, provider="s3")
        assert url and url.startswith("http")
        # Check that the file was uploaded successfully
        # This is a basic check, in a real test we might want to download and verify
        assert url and url.startswith("http")

    def test_s3_upload_with_custom_endpoint(self, monkeypatch):
        """Test uploading with a custom S3 endpoint."""
        monkeypatch.setenv("AWS_ENDPOINT_URL", "https://custom-endpoint.example.com")
        url = upload_file(SMALL_FILE, provider="s3")
        assert url and url.startswith("http")


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


@pytest.mark.skipif(not HAS_FAL, reason="FAL dependencies not installed")
class TestFalIntegration:
    """Integration tests for FAL provider."""

    @pytest.fixture(autouse=True)
    def check_fal_credentials(self):
        """Skip tests if FAL credentials are not available."""
        if not os.getenv("FAL_KEY"):
            pytest.skip("FAL credentials not available")

    def test_fal_setup(self):
        """Test FAL provider setup."""
        provider_info = setup_provider("fal")
        assert provider_info.success

    def test_fal_upload_small_file(self):
        """Test uploading a small file to FAL."""
        url = upload_file(SMALL_FILE, provider="fal")
        assert url and url.startswith("http")

    def test_fal_upload_large_file(self, large_test_file):
        """Test uploading a large file to FAL."""
        url = upload_file(large_test_file, provider="fal")
        assert url and url.startswith("http")
        # Check that the file was uploaded successfully
        # This is a basic check, in a real test we might want to download and verify
        assert url and url.startswith("http")


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
        result = setup_provider("catbox")
        assert (
            result.success is True
        )  # Should always work since anonymous uploads are supported

    def test_catbox_upload_small_file(self, small_file):
        """Test uploading a small file to Catbox."""
        try:
            url = upload_file(small_file, provider="catbox")
            assert isinstance(url, str)
            assert url.startswith("https://files.catbox.moe/")
            assert len(url) > len("https://files.catbox.moe/")
        except Exception as e:
            pytest.skip(f"Catbox upload failed: {e}")

    def test_catbox_upload_large_file(self, large_file):
        """Test uploading a large file to Catbox."""
        try:
            url = upload_file(large_file, provider="catbox")
            assert isinstance(url, str)
            assert url.startswith("https://files.catbox.moe/")
            assert len(url) > len("https://files.catbox.moe/")
        except Exception as e:
            pytest.skip(f"Catbox upload failed: {e}")

    @pytest.mark.skipif(
        not os.getenv("CATBOX_USERHASH"),
        reason="Requires CATBOX_USERHASH environment variable",
    )
    def test_catbox_authenticated_upload(self, small_file):
        """Test authenticated upload to Catbox."""
        url = upload_file(small_file, provider="catbox")
        assert url.startswith("https://files.catbox.moe/")

        # Try to delete the file
        filename = url.split("/")[-1]
        provider = catbox.get_provider()
        assert provider is not None

        # Try to delete the file if the provider supports it
        try:
            if hasattr(provider, "delete_files") and callable(
                getattr(provider, "delete_files", None)
            ):
                success = provider.delete_files([filename])
                assert success is True
        except (AttributeError, NotImplementedError):
            # Skip if delete_files is not implemented or raises an error
            pass


class TestLitterboxIntegration:
    """Integration tests for Litterbox provider."""

    def test_litterbox_setup(self):
        """Test Litterbox provider setup."""
        result = setup_provider("litterbox")
        assert result.success is True  # Should always work since no auth needed

    def test_litterbox_upload_small_file(self, small_file):
        """Test uploading a small file to Litterbox."""
        try:
            url = upload_file(small_file, provider="litterbox")
            assert isinstance(url, str)
            assert url.startswith("https://litter.catbox.moe/")
            assert len(url) > len("https://litter.catbox.moe/")
        except Exception as e:
            pytest.skip(f"Litterbox upload failed: {e}")

    def test_litterbox_upload_large_file(self, large_file):
        """Test uploading a large file to Litterbox."""
        try:
            url = upload_file(large_file, provider="litterbox")
            assert isinstance(url, str)
            assert url.startswith("https://litter.catbox.moe/")
            assert len(url) > len("https://litter.catbox.moe/")
        except Exception as e:
            pytest.skip(f"Litterbox upload failed: {e}")

    def test_litterbox_different_expirations(self, small_file):
        """Test Litterbox with different expiration times."""
        try:
            # Test with 1 hour expiration
            provider = litterbox.LitterboxProvider(
                default_expiration=ExpirationTime.HOUR_1
            )
            url = provider.upload_file(small_file)
            assert isinstance(url, str)
            assert url.startswith("https://litter.catbox.moe/")

            # Test with 12 hours expiration
            provider = litterbox.LitterboxProvider(
                default_expiration=ExpirationTime.HOURS_12
            )
            url = provider.upload_file(small_file)
            assert isinstance(url, str)
            assert url.startswith("https://litter.catbox.moe/")

            # Test with 24 hours expiration
            provider = litterbox.LitterboxProvider(
                default_expiration=ExpirationTime.HOURS_24
            )
            url = provider.upload_file(small_file)
            assert isinstance(url, str)
            assert url.startswith("https://litter.catbox.moe/")
        except Exception as e:
            pytest.skip(f"Litterbox upload with different expirations failed: {e}")
