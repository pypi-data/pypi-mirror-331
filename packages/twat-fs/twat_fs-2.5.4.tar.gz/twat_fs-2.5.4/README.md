---
this_file: README.md
---

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

## Recent Improvements

The codebase has undergone significant refactoring to improve maintainability and extensibility:

* **Centralized Utilities**: Created a `utils.py` module with shared functionality for all providers
* **Standardized Implementation**: All providers now follow consistent patterns and inherit from `BaseProvider`
* **Improved Error Handling**: Enhanced error classification and handling across all providers
* **Provider Templates**: Created templates for simple and authenticated providers to standardize implementation
* **Better Type Safety**: Improved type annotations and protocol compatibility
* **Consistent Logging**: Standardized logging patterns for better debugging and monitoring
* **Factory Pattern**: Implemented a factory pattern for provider instantiation to simplify creation and standardize error handling
* **Async/Sync Utilities**: Created standardized utilities for async/sync conversion to ensure consistent patterns across providers
* **Comprehensive Testing**: Added thorough unit tests for utility functions covering edge cases and error conditions
* **Provider Base Classes**: Created base classes to reduce inheritance boilerplate and standardize provider implementation

## Current Status

The project is in active development with several key areas of focus:

* **Fixing Type Annotation Issues**: Addressing incompatible return types and type mismatches
* **Resolving Test Failures**: Fixing failing unit tests in the utils and async_utils modules
* **Improving Exception Handling**: Implementing proper exception chaining across providers
* **Addressing Linter Issues**: Fixing various linter warnings, particularly in cleanup.py and cli.py
* **Expanding Provider Support**: Planning implementation of additional upload providers

## Project Documentation

The project maintains several key documentation files:

* **README.md** (this file): Overview, installation, usage, and architecture
* **CHANGELOG.md**: Detailed record of all changes and improvements
* **TODO.md**: Prioritized list of upcoming tasks and features

These files are regularly updated to reflect the current state of the project.

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

### Using the Factory Pattern

```python
from twat_fs.upload_providers.factory import ProviderFactory

# Get a provider instance
factory = ProviderFactory()
provider = factory.get_provider("s3")

# Upload a file
result = provider.upload_file("path/to/file.txt")
print(f"File uploaded to: {result.url}")

# Get all available providers
available_providers = factory.list_available_providers()
print(f"Available providers: {available_providers}")
```

### Async/Sync Conversion

```python
from twat_fs.upload_providers.async_utils import to_sync, to_async, run_async

# Convert an async function to sync
@to_sync
async def async_function():
    # Async implementation
    return "result"

# Use the sync version
result = async_function()  # No need for await

# Convert a sync function to async
@to_async
def sync_function():
    # Sync implementation
    return "result"

# Use the async version
async def main():
    result = await sync_function()

# Run an async function in a sync context
result = run_async(async_function())
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

5. **BaseProvider**: Abstract base class for all providers
   * Implements common functionality
   * Standardizes method signatures
   * Provides default implementations
   * Reduces code duplication

6. **Factory Pattern**: Centralized provider instantiation
   * Simplifies provider creation
   * Standardizes error handling during initialization
   * Reduces code duplication in provider creation
   * Provides a cleaner API for getting provider instances

7. **Async/Sync Utilities**: Standardized conversion patterns
   * `run_async`: For running coroutines in a synchronous context
   * `to_sync`: Decorator for converting async functions to sync
   * `to_async`: Decorator for converting sync functions to async
   * `gather_with_concurrency`: For limiting concurrent async operations
   * `AsyncContextManager`: Base class for implementing async context managers
   * `with_async_timeout`: Decorator for adding timeouts to async functions

8. **Utility Functions**: Shared functionality across providers
   * File validation and handling
   * HTTP response processing
   * Credential management
   * Logging standardization

### Type System

Strong typing throughout with runtime checks:

* Type hints for all public APIs
* Runtime protocol verification
* Custom types for provider-specific data
* Error type hierarchy

## Implementing a New Provider

To add a new storage provider, use one of the provided templates in the `templates` directory:

* `simple_provider_template.py`: For providers without authentication
* `authenticated_provider_template.py`: For providers requiring credentials

These templates include:
* Standard imports and class structure
* Consistent error handling patterns
* Proper use of utility functions
* Documentation templates and type annotations
* Module-level functions implementing the Provider protocol

Example implementation (simplified):

```python
from pathlib import Path
from typing import Any, BinaryIO, ClassVar
from twat_fs.upload_providers.simple import BaseProvider
from twat_fs.upload_providers.protocols import ProviderHelp, ProviderClient
from twat_fs.upload_providers.utils import (
    create_provider_help,
    log_upload_attempt,
    standard_upload_wrapper,
)
from twat_fs.upload_providers.types import UploadResult

# Provider-specific help messages
PROVIDER_HELP: ProviderHelp = create_provider_help(
    setup_instructions="Setup instructions for users...",
    dependency_info="Additional dependencies needed..."
)

class YourProvider(BaseProvider):
    """Provider for your service."""
    
    # Class variables
    PROVIDER_HELP: ClassVar[ProviderHelp] = PROVIDER_HELP
    provider_name = "your_provider"
    
    def _do_upload(self, file: BinaryIO) -> str:
        """Implement the actual upload logic."""
        # Your implementation here
        ...
        return "https://example.com/uploaded_file"
        
    def upload_file_impl(self, file: BinaryIO) -> UploadResult:
        """Handle the file upload process."""
        try:
            url = self._do_upload(file)
            log_upload_attempt(self.provider_name, file.name, success=True)
            return convert_to_upload_result(url, metadata={"provider": self.provider_name})
        except Exception as e:
            log_upload_attempt(self.provider_name, file.name, success=False, error=e)
            raise

# Module-level functions
def get_credentials() -> dict[str, Any] | None:
    """Get provider credentials."""
    return None  # For simple providers

def get_provider() -> ProviderClient | None:
    """Initialize and return the provider."""
    return YourProvider()

def upload_file(local_path: str | Path, remote_path: str | Path | None = None, **kwargs) -> UploadResult:
    """Upload a file using this provider."""
    return standard_upload_wrapper(
        provider=get_provider(),
        provider_name="your_provider",
        local_path=local_path,
        remote_path=remote_path,
        **kwargs
    )
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/test_utils.py tests/test_async_utils.py -v

# Run with coverage
python -m pytest --cov=twat_fs
```

### Linting

```bash
# Run linter with fixes
ruff check --output-format=github --fix --unsafe-fixes .

# Format code
ruff format --respect-gitignore --target-version py312 .
```

### Project Status

Run the cleanup script to check the status of lints and tests:

```bash
./cleanup.py status
```

## Contributing

Contributions are welcome! Please check the TODO.md file for current priorities and planned features.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting to ensure code quality
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

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
