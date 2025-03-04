# twat-fs

File system utilities for twat, focusing on robust and extensible file upload capabilities with multiple provider support.

## Rationale

`twat-fs` provides a unified interface for uploading files to various storage providers while addressing common challenges:

* **Provider Flexibility**: Seamlessly switch between storage providers without code changes
* **Smart Fallback**: Intelligent retry and fallback between providers:
  * One retry with exponential backoff for temporary failures
  * Automatic fallback to next provider for permanent failures
  * Clear distinction between retryable and non-retryable errors
* **URL Validation**: Ensures returned URLs are accessible before returning them
* **Progressive Enhancement**: Start simple with zero configuration (simple providers), scale up to advanced providers (S3, Dropbox) as needed
* **Developer Experience**: Clear interfaces, comprehensive type hints, and runtime checks
* **Extensibility**: Well-defined provider protocol for adding new storage backends

## Quick Start

### Installation

Basic installation with simple providers:

```bash
uv pip install twat-fs
```

Install with all providers and development tools:

```bash
uv pip install 'twat-fs[all,dev]'
```

### Basic Usage

```python
from twat_fs import upload_file

# Simple upload (uses catbox.moe by default)
url = upload_file("path/to/file.txt")

# Specify provider with fallback
url = upload_file("path/to/file.txt", provider=["s3", "dropbox", "catbox"])

# Handle provider-specific errors
from twat_fs.upload_providers.core import RetryableError, NonRetryableError

try:
    url = upload_file("file.txt", provider="s3")
except RetryableError as e:
    print(f"Temporary error with {e.provider}: {e}")
except NonRetryableError as e:
    print(f"Permanent error with {e.provider}: {e}")
```

### Command Line Interface

```bash
# Simple upload
python -m twat_fs upload_file path/to/file.txt

# Specify provider with fallback
python -m twat_fs upload_file path/to/file.txt --provider s3,dropbox,catbox

# Disable fallback (fail immediately if provider fails)
python -m twat_fs upload_file path/to/file.txt --provider s3 --fragile

# Check provider setup
python -m twat_fs setup provider s3
python -m twat_fs setup all
```

## Provider Configuration

### Provider Fallback System

The package implements a robust provider fallback system:

1. **Circular Fallback**: When using multiple providers, if a provider fails, the system will:
   * Try the next provider in the list
   * If all remaining providers fail, start over from the beginning of the full provider list
   * Continue until all providers have been tried once
   * Each provider is only tried once to avoid infinite loops

2. **Fragile Mode**: For cases where fallback is not desired:
   * Use the `--fragile` flag in CLI: `--fragile`
   * In code: `upload_file(..., fragile=True)`
   * System will fail immediately if the requested provider fails
   * No fallback attempts will be made

Example fallback scenarios:

```python
# Full circular fallback (if E fails, tries F, G, A, B, C, D)
url = upload_file("file.txt", provider="E")

# Fragile mode (fails immediately if E fails)
url = upload_file("file.txt", provider="E", fragile=True)

# Custom provider list with circular fallback
# If C fails, tries A, then B
url = upload_file("file.txt", provider=["C", "A", "B"])
```

### Simple Providers (No Configuration Required)

The following providers work out of the box with no configuration:

* **catbox.moe**: General file uploads (default)
* **litterbox.catbox.moe**: Temporary file uploads with expiration
* **www0x0.st**: General file uploads
* **uguu.se**: Temporary file uploads
* **bashupload.com**: General file uploads
* **filebin.net**: Temporary file uploads (6-day expiration)
* **pixeldrain.com**: General file uploads

### Dropbox

```bash
export DROPBOX_ACCESS_TOKEN="your_token_here"
# Optional OAuth2 configuration
export DROPBOX_REFRESH_TOKEN="refresh_token"
export DROPBOX_APP_KEY="app_key"
export DROPBOX_APP_SECRET="app_secret"
```

### AWS S3

```bash
# Required
export AWS_S3_BUCKET="your_bucket"
export AWS_DEFAULT_REGION="us-east-1"

# Authentication (choose one)
export AWS_ACCESS_KEY_ID="key_id"
export AWS_SECRET_ACCESS_KEY="secret_key"
# Or use AWS CLI: aws configure
# Or use IAM roles in AWS infrastructure

# Optional
export AWS_ENDPOINT_URL="custom_endpoint"  # For S3-compatible services
export AWS_S3_PATH_STYLE="true"  # For path-style endpoints
export AWS_ROLE_ARN="role_to_assume"
```

### FAL.ai

```bash
export FAL_KEY="your_key_here"
```

## Architecture

### Provider System

The package uses a provider-based architecture with these key components:

1. **Provider Registry**: Central registry of available providers
   * Maintains provider preference order
   * Handles lazy loading of provider modules
   * Provides runtime protocol checking
   * Manages provider fallback chain

2. **Provider Protocol**: Formal interface that all providers must implement
   * Credentials management
   * Client initialization
   * File upload functionality
   * Help and setup information
   * Error classification (retryable vs. non-retryable)

3. **Provider Client**: The actual implementation that handles uploads
   * Provider-specific upload logic
   * Error handling and retries
   * URL validation
   * Progress tracking (where supported)

4. **Error Handling**: Structured error hierarchy
   * RetryableError: Temporary failures (rate limits, timeouts)
   * NonRetryableError: Permanent failures (auth, invalid files)
   * Automatic retry with exponential backoff
   * Provider fallback for permanent failures

### Type System

Strong typing throughout with runtime checks:

* Type hints for all public APIs
* Runtime protocol verification
* Custom types for provider-specific data
* Error type hierarchy

## Implementing a New Provider

To add a new storage provider, create a module in `twat_fs/upload_providers/` that implements the Provider protocol:

```python
from pathlib import Path
from typing import Any, TypedDict
from twat_fs.upload_providers import ProviderClient, Provider

# Provider-specific help messages
PROVIDER_HELP = {
    "setup": """Setup instructions for users...""",
    "deps": """Additional dependencies needed..."""
}

def get_credentials() -> dict[str, Any] | None:
    """
    Get provider credentials from environment.
    Return None if not configured.
    """
    # Implement credential checking
    ...

def get_provider() -> ProviderClient | None:
    """
    Initialize and return the provider client.
    Only import provider-specific dependencies here.
    """
    creds = get_credentials()
    if not creds:
        return None
    
    try:
        # Initialize your provider client
        client = YourProviderClient(creds)
        return client
    except Exception:
        return None

def upload_file(local_path: str | Path, remote_path: str | Path | None = None) -> str:
    """
    Upload a file and return its public URL.
    This is a convenience wrapper around get_provider().
    """
    client = get_provider()
    if not client:
        raise ValueError("Provider not configured")
    return client.upload_file(local_path, remote_path)

# Your provider client implementation
class YourProviderClient:
    def upload_file(
        self, 
        local_path: str | Path, 
        remote_path: str | Path | None = None
    ) -> str:
        """Implement the actual upload logic."""
        ...
```

Then add your provider to `PROVIDERS_PREFERENCE` in `upload_providers/__init__.py`.

## Development

### Setup Environment

```bash
# Install development tools
uv pip install uv

# Create and activate environment
uv venv
source .venv/bin/activate

# Install in development mode with all extras
uv pip install -e '.[dev,all,test]'
```

### Code Quality

```bash
# Format code
python -m ruff format src tests
python -m ruff check --fix --unsafe-fixes src tests

# Run type checks
python -m mypy src tests

# Run tests
python -m pytest tests
python -m pytest --cov=src/twat_fs tests  # with coverage

# Quick development cycle
./cleanup.py install  # Set up environment
./cleanup.py status  # Run all checks
```

### Publish

Make sure to have in your env:

```bash
export UV_PUBLISH_TOKEN="${PYPI_TOKEN}"
```

Build and publish:

```bash
VER="v1.7.9" && echo "$VER" > VERSION.txt && git commit -am "$VER" && git tag "$VER"
uv build && uv publish
```

### Testing

The test suite includes:

* Unit tests for each provider
* Integration tests with real services
* Performance tests for large files
* Error condition tests
* Type checking tests

When adding a new provider:

1. Add unit tests in `tests/test_providers/`
2. Add integration tests in `tests/test_integration.py`
3. Add performance tests if relevant
4. Update provider discovery tests

## Error Handling & Troubleshooting

### Error Types

The package uses a structured error hierarchy for better error handling:

```python
from twat_fs.upload_providers.core import (
    UploadError,              # Base class for all upload errors
    RetryableError,           # Temporary failures that should be retried
    NonRetryableError,        # Permanent failures that trigger fallback
)
```

### Common Issues

1. **Temporary Failures (RetryableError)**
   * Rate limiting
   * Network timeouts
   * Server errors (503, 504)
   * Connection resets
   ```python
   try:
       url = upload_file("file.txt")
   except RetryableError as e:
       print(f"Temporary error with {e.provider}: {e}")
       # Will be retried automatically with exponential backoff
   ```

2. **Permanent Failures (NonRetryableError)**
   * Authentication failures
   * Invalid files
   * Missing permissions
   * Provider not available
   ```python
   try:
       url = upload_file("file.txt", provider=["s3", "dropbox"])
   except NonRetryableError as e:
       print(f"All providers failed. Last error from {e.provider}: {e}")
   ```

3. **URL Validation**
   * All returned URLs are validated with HEAD request
   * Follows redirects
   * Verifies accessibility
   * Retries on temporary failures
   ```python
   # URL is guaranteed to be accessible when returned
   url = upload_file("file.txt")
   ```

### Provider Status Checking

Use the setup commands to diagnose provider issues:

```bash
# Check specific provider
python -m twat_fs setup provider s3

# Check all providers
python -m twat_fs setup all
```

### Logging

The package uses `loguru` for structured logging:

```python
from loguru import logger

# Set log level
logger.level("DEBUG")

# Add file handler
logger.add("twat_fs.log", rotation="1 day")

# Log format includes provider info
logger.add(
    sys.stderr,
    format="{time} {level} [{extra[provider]}] {message}"
)
```

### Debugging Provider Issues

When implementing a new provider:

1. Enable debug logging:

```python
import logging
logging.getLogger("twat_fs").setLevel(logging.DEBUG)
```

2. Use the provider test helper:

```python
from twat_fs.testing import ProviderTestHelper

helper = ProviderTestHelper("your_provider")
helper.test_provider_implementation()  # Checks protocol compliance
helper.test_provider_functionality()   # Tests basic operations
```

3. Check provider initialization:

```python
from twat_fs.upload_providers import get_provider_module

provider = get_provider_module("your_provider")
print(provider.get_credentials())  # Check credential loading
print(provider.get_provider())     # Check client initialization
```

## License

MIT License

.

## extra

```bash
for PROVIDER in $(twat fs upload_provider list 2>/dev/null); do URL="$(twat fs upload "./src/twat_fs/data/test.jpg" --provider "$PROVIDER")"; echo "[$PROVIDER]($URL)"; done
```

```
Error: Upload failed: Failed to upload with catbox: Unexpected error: URL validation failed (status 503)
[catbox]()
[litterbox](https://litter.catbox.moe/8a6jf0.jpg)
[fal](https://v3.fal.media/files/monkey/Kd6SwMGEIbxMIFPihlFQL_test.jpg)
[bashupload](https://bashupload.com/TTHlX/test.jpg?download=1)
[uguu](https://d.uguu.se/RrhFSqLP.jpg)
[www0x0](https://0x0.st/8qUT.jpg)
[filebin](https://filebin.net/twat-fs-1739859030-enq2xe/test.jpg)
```
