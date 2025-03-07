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

* **Fixed Provider Instantiation**: Improved the `create_provider_instance` function to correctly handle credential management and provider instantiation order
* **Centralized Utilities**: Created a `utils.py` module with shared functionality for all providers
* **Standardized Implementation**: All providers now follow consistent patterns and inherit from `BaseProvider`
* **Improved Error Handling**: Enhanced error classification and handling across all providers with `RetryableError` and `NonRetryableError` classes
* **Provider Templates**: Created templates for simple and authenticated providers to standardize implementation
* **Better Type Safety**: Improved type annotations and protocol compatibility
* **Consistent Logging**: Standardized logging patterns with `log_upload_attempt` function for better debugging and monitoring
* **Factory Pattern**: Implemented a factory pattern for provider instantiation to simplify creation and standardize error handling
* **Async/Sync Utilities**: Created standardized utilities for async/sync conversion to ensure consistent patterns across providers
* **Comprehensive Testing**: Added thorough unit tests for utility functions covering edge cases and error conditions
* **Provider Base Classes**: Created base classes to reduce inheritance boilerplate and standardize provider implementation
* **URL Validation**: Improved URL validation to ensure returned URLs are accessible before returning them

## Current Status

The project is in active development with several key areas of focus:

* **Fixing Type Annotation Issues**: Addressing incompatible return types in async methods, type mismatches in factory.py and simple.py, and ensuring proper typing for async/await conversions
* **Resolving Remaining Test Failures**: Fixing failing unit tests, particularly in TestLogUploadAttempt and TestGatherWithConcurrency
* **Addressing Boolean Argument Issues**: Converting boolean positional arguments to keyword-only arguments to fix FBT001/FBT002 linter errors
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

### Provider Instantiation

The package uses a robust provider instantiation system that follows this order:

1. If no credentials are provided, try to get them from the provider class
2. If the provider class has a `get_provider` method, use that
3. If `get_provider` fails, fall back to direct instantiation

This ensures that providers are instantiated correctly regardless of how they're configured:

```python
from twat_fs.upload_providers.utils import create_provider_instance
from twat_fs.upload_providers import s3

# Get a provider instance with explicit credentials
credentials = {"AWS_S3_BUCKET": "my-bucket", "AWS_ACCESS_KEY_ID": "key", "AWS_SECRET_ACCESS_KEY": "secret"}
provider = create_provider_instance(s3.S3Provider, credentials)

# Get a provider instance using environment variables
provider = create_provider_instance(s3.S3Provider)
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
```

## Development

### Running Tests and Linting

The project uses `cleanup.py` for managing repository tasks and maintaining code quality:

```bash
# Check the current state of the repository
python ./cleanup.py status

# Install dependencies
uv pip install -e '.[test,dev]'

# Run tests
python -m pytest

# Run linting
ruff check --output-format=github --fix --unsafe-fixes . && ruff format --respect-gitignore --target-version py312 .
```

### Current Issues

Based on the latest linting and test results, the following issues need to be addressed:

1. **Missing Dependencies for Tests**:
   - Some tests require additional dependencies: 'fal_client', 'botocore', 'responses'
   - Need to install these dependencies or implement proper test skipping
   - Affected files: `tests/test_integration.py`, `tests/test_s3_advanced.py`, `tests/test_upload.py`

2. **Boolean Argument Issues**:
   - FBT001/FBT002 linter errors for boolean positional arguments
   - FBT003 linter errors for boolean positional values in function calls
   - Need to convert boolean positional arguments to keyword-only arguments

3. **Type Annotation Issues**:
   - Incompatible return types in async methods
   - Type mismatches in factory.py and simple.py
   - Missing type annotations for variables in simple.py
   - Improper typing for async/await conversions

4. **Exception Handling Issues**:
   - B904 linter errors: Need to use `raise ... from err` in exception handling
   - S101 linter errors: Use of `assert` detected in core.py

5. **Function Complexity Issues**:
   - Functions with too many arguments (PLR0913)
   - Complex functions with too many branches/statements/returns (C901, PLR0911, PLR0912, PLR0915)
   - Need to refactor these functions for better maintainability

### Contributing

Contributions are welcome! Please check the TODO.md file for current priorities and open issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Example Provider Results

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
