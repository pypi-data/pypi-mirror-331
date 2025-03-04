# this_file: tests/test_utils.py

"""
Unit tests for the utils.py module.
Tests each utility function thoroughly, covering edge cases and error conditions.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import requests
import aiohttp

from twat_fs.upload_providers.utils import (
    create_provider_help,
    safe_file_handle,
    validate_file,
    handle_http_response,
    get_env_credentials,
    create_provider_instance,
    standard_upload_wrapper,
    log_upload_attempt,
)
from twat_fs.upload_providers.core import RetryableError, NonRetryableError
from twat_fs.upload_providers.protocols import ProviderClient, Provider
from twat_fs.upload_providers.types import UploadResult


class TestCreateProviderHelp:
    """Tests for the create_provider_help function."""

    def test_create_provider_help(self):
        """Test that create_provider_help returns a correctly formatted dictionary."""
        setup = "Test setup instructions"
        deps = "Test dependency info"

        result = create_provider_help(setup, deps)

        assert result == {"setup": setup, "deps": deps}
        assert isinstance(result, dict)


class TestSafeFileHandle:
    """Tests for the safe_file_handle context manager."""

    def test_safe_file_handle_with_valid_file(self):
        """Test that safe_file_handle correctly opens and closes a file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        try:
            with safe_file_handle(temp_path) as file:
                assert file.read() == b"test content"
                assert not file.closed

            # File should be closed after exiting the context manager
            assert file.closed
        finally:
            os.unlink(temp_path)

    def test_safe_file_handle_with_nonexistent_file(self):
        """Test that safe_file_handle raises FileNotFoundError for nonexistent files."""
        with pytest.raises(FileNotFoundError):
            with safe_file_handle("/path/to/nonexistent/file"):
                pass

    def test_safe_file_handle_with_directory(self):
        """Test that safe_file_handle raises ValueError for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError):
                with safe_file_handle(temp_dir):
                    pass


class TestValidateFile:
    """Tests for the validate_file function."""

    def test_validate_file_with_valid_file(self):
        """Test that validate_file does not raise exceptions for valid files."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Should not raise any exceptions
            validate_file(Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_validate_file_with_nonexistent_file(self):
        """Test that validate_file raises FileNotFoundError for nonexistent files."""
        with pytest.raises(FileNotFoundError):
            validate_file(Path("/path/to/nonexistent/file"))

    def test_validate_file_with_directory(self):
        """Test that validate_file raises ValueError for directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError):
                validate_file(Path(temp_dir))

    @mock.patch("os.access", return_value=False)
    def test_validate_file_with_unreadable_file(self, mock_access):
        """Test that validate_file raises PermissionError for unreadable files."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with pytest.raises(PermissionError):
                validate_file(Path(temp_path))
        finally:
            os.unlink(temp_path)


class TestHandleHttpResponse:
    """Tests for the handle_http_response function."""

    def test_handle_http_response_with_200_requests(self):
        """Test that handle_http_response does not raise exceptions for 200 status code with requests."""
        response = mock.Mock(spec=requests.Response)
        response.status_code = 200

        # Should not raise any exceptions
        handle_http_response(response, "test_provider")

    def test_handle_http_response_with_200_aiohttp(self):
        """Test that handle_http_response does not raise exceptions for 200 status code with aiohttp."""
        response = mock.Mock(spec=aiohttp.ClientResponse)
        response.status = 200

        # Should not raise any exceptions
        handle_http_response(response, "test_provider")

    def test_handle_http_response_with_429_requests(self):
        """Test that handle_http_response raises RetryableError for 429 status code with requests."""
        response = mock.Mock(spec=requests.Response)
        response.status_code = 429
        response.text = "Rate limited"

        with pytest.raises(RetryableError):
            handle_http_response(response, "test_provider")

    def test_handle_http_response_with_429_aiohttp(self):
        """Test that handle_http_response raises RetryableError for 429 status code with aiohttp."""
        response = mock.Mock(spec=aiohttp.ClientResponse)
        response.status = 429

        with pytest.raises(RetryableError):
            handle_http_response(response, "test_provider")

    def test_handle_http_response_with_503_requests(self):
        """Test that handle_http_response raises RetryableError for 503 status code with requests."""
        response = mock.Mock(spec=requests.Response)
        response.status_code = 503

        with pytest.raises(RetryableError):
            handle_http_response(response, "test_provider")

    def test_handle_http_response_with_400_requests(self):
        """Test that handle_http_response raises NonRetryableError for 400 status code with requests."""
        response = mock.Mock(spec=requests.Response)
        response.status_code = 400

        with pytest.raises(NonRetryableError):
            handle_http_response(response, "test_provider")

    def test_handle_http_response_with_other_error_requests(self):
        """Test that handle_http_response raises RetryableError for other error status codes with requests."""
        response = mock.Mock(spec=requests.Response)
        response.status_code = 500

        with pytest.raises(RetryableError):
            handle_http_response(response, "test_provider")


class TestGetEnvCredentials:
    """Tests for the get_env_credentials function."""

    def test_get_env_credentials_with_all_required_vars(self):
        """Test that get_env_credentials returns a dictionary with all required variables."""
        with mock.patch.dict(
            os.environ, {"TEST_VAR1": "value1", "TEST_VAR2": "value2"}
        ):
            result = get_env_credentials(["TEST_VAR1", "TEST_VAR2"])

            assert result == {"TEST_VAR1": "value1", "TEST_VAR2": "value2"}

    def test_get_env_credentials_with_missing_required_vars(self):
        """Test that get_env_credentials returns None if any required variable is missing."""
        with mock.patch.dict(os.environ, {"TEST_VAR1": "value1"}):
            result = get_env_credentials(["TEST_VAR1", "TEST_VAR2"])

            assert result is None

    def test_get_env_credentials_with_optional_vars(self):
        """Test that get_env_credentials includes optional variables if present."""
        with mock.patch.dict(
            os.environ,
            {
                "TEST_VAR1": "value1",
                "TEST_VAR2": "value2",
                "TEST_VAR3": "value3",
            },
        ):
            result = get_env_credentials(
                ["TEST_VAR1", "TEST_VAR2"],
                ["TEST_VAR3", "TEST_VAR4"],
            )

            assert result == {
                "TEST_VAR1": "value1",
                "TEST_VAR2": "value2",
                "TEST_VAR3": "value3",
            }

    def test_get_env_credentials_with_missing_optional_vars(self):
        """Test that get_env_credentials does not include missing optional variables."""
        with mock.patch.dict(
            os.environ, {"TEST_VAR1": "value1", "TEST_VAR2": "value2"}
        ):
            result = get_env_credentials(
                ["TEST_VAR1", "TEST_VAR2"],
                ["TEST_VAR3", "TEST_VAR4"],
            )

            assert result == {"TEST_VAR1": "value1", "TEST_VAR2": "value2"}


class TestCreateProviderInstance:
    """Tests for the create_provider_instance function."""

    def test_create_provider_instance_with_get_provider(self):
        """Test that create_provider_instance uses get_provider if available."""
        mock_provider = mock.Mock(spec=Provider)
        mock_provider.__name__ = "MockProvider"
        mock_client = mock.Mock(spec=ProviderClient)
        mock_provider.get_provider.return_value = mock_client

        result = create_provider_instance(mock_provider)

        assert result == mock_client
        mock_provider.get_provider.assert_called_once()

    def test_create_provider_instance_with_direct_instantiation(self):
        """Test that create_provider_instance falls back to direct instantiation."""
        mock_provider = mock.Mock(spec=Provider)
        mock_provider.__name__ = "MockProvider"
        mock_provider.get_provider.side_effect = AttributeError

        result = create_provider_instance(mock_provider)

        assert result == mock_provider.return_value
        mock_provider.assert_called_once()

    def test_create_provider_instance_with_credentials(self):
        """Test that create_provider_instance uses provided credentials."""
        mock_provider = mock.Mock(spec=Provider)
        mock_provider.__name__ = "MockProvider"
        credentials = {"key": "value"}

        create_provider_instance(mock_provider, credentials)

        # Should not call get_credentials
        mock_provider.get_credentials.assert_not_called()

    def test_create_provider_instance_with_no_credentials(self):
        """Test that create_provider_instance gets credentials if not provided."""
        mock_provider = mock.Mock(spec=Provider)
        mock_provider.__name__ = "MockProvider"
        mock_provider.get_credentials.return_value = {"key": "value"}

        # Add debug prints

        create_provider_instance(mock_provider)

        # Add debug prints

        mock_provider.get_credentials.assert_called_once()

    def test_create_provider_instance_with_error(self):
        """Test that create_provider_instance returns None if initialization fails."""
        mock_provider = mock.Mock(spec=Provider)
        mock_provider.__name__ = "MockProvider"
        mock_provider.get_provider.side_effect = Exception("Test error")

        result = create_provider_instance(mock_provider)

        assert result is None


class TestStandardUploadWrapper:
    """Tests for the standard_upload_wrapper function."""

    def test_standard_upload_wrapper_with_valid_provider(self):
        """Test that standard_upload_wrapper calls upload_file on the provider."""
        mock_provider = mock.Mock(spec=ProviderClient)
        mock_provider.upload_file.return_value = UploadResult(
            url="https://example.com/file",
            metadata={"provider": "test_provider"},
        )

        result = standard_upload_wrapper(
            mock_provider,
            "test_provider",
            "test_file.txt",
            "remote_file.txt",
            unique=True,
            force=True,
            upload_path="test_path",
            extra_arg="extra_value",
        )

        assert result == mock_provider.upload_file.return_value
        mock_provider.upload_file.assert_called_once_with(
            "test_file.txt",
            "remote_file.txt",
            unique=True,
            force=True,
            upload_path="test_path",
            extra_arg="extra_value",
        )

    def test_standard_upload_wrapper_with_none_provider(self):
        """Test that standard_upload_wrapper raises ValueError if provider is None."""
        with pytest.raises(ValueError):
            standard_upload_wrapper(
                None,
                "test_provider",
                "test_file.txt",
            )


class TestLogUploadAttempt:
    """Tests for the log_upload_attempt function."""

    @mock.patch("loguru.logger.info")
    def test_log_upload_attempt_success(self, mock_logger_info):
        """Test that log_upload_attempt logs success correctly."""
        log_upload_attempt("test_provider", "test_file.txt", True)

        mock_logger_info.assert_called_once()
        assert "Successfully uploaded" in mock_logger_info.call_args[0][0]

    @mock.patch("loguru.logger.error")
    def test_log_upload_attempt_failure(self, mock_logger_error):
        """Test that log_upload_attempt logs failure correctly."""
        error = Exception("Test error")
        log_upload_attempt("test_provider", "test_file.txt", False, error)

        mock_logger_error.assert_called_once()
        assert "Failed to upload" in mock_logger_error.call_args[0][0]
        assert "Test error" in mock_logger_error.call_args[0][0]
