---
this_file: TODO.md
---

# TODO

Tip: Periodically run `./cleanup.py status` to see results of lints and tests.

## Phase 1

- [ ] Fix type annotation issues identified by linter
  - Address incompatible return types in async methods
  - Fix type mismatches in factory.py and simple.py
  - Ensure proper typing for async/await conversions
  - Resolve "possibly unbound" variable warnings in upload.py
  - Rename TypeVar "T" and "R" to "T_co" and "R_co" in core.py
  - Add ClassVar annotations to mutable class attributes

## Phase 2

- [ ] Fix failing unit tests
  - Fix TestCreateProviderInstance tests with proper mock setup (add '__name__' attribute to mocks)
  - Fix TestLogUploadAttempt.test_log_upload_attempt_success test (logger.info not being called)
  - Fix TestGatherWithConcurrency.test_gather_with_concurrency_with_exceptions test (RuntimeError instead of ValueError)

## Phase 3
- [ ] Fix exception handling issues
  - Use proper exception chaining with `raise ... from err` or `raise ... from None`
  - Fix B904 linter errors in multiple provider files

- [ ] Fix cleanup.py linter issues
  - Fix DTZ005: Add timezone to datetime.datetime.now() calls
  - Fix FBT001/FBT002: Boolean-typed positional arguments
  - Fix S603/S607: Subprocess call security issues

## Medium Priority

- [ ] Refine HTTP response handling across providers
  - Ensure all providers use `handle_http_response()` consistently
  - Standardize handling of various HTTP status codes
  - Improve handling of rate limits (429) and other non-200 responses

- [ ] Fix function complexity issues
  - Refactor complex functions in cli.py and upload.py
  - Address C901, PLR0911, PLR0912, PLR0915 linter errors
  - Split large functions into smaller, more focused functions

- [ ] Fix boolean argument issues
  - Address FBT001, FBT002, FBT003 linter errors
  - Use keyword arguments for boolean parameters
  - Refactor functions with too many arguments (PLR0913)

- [ ] Document best practices for creating new providers
  - Create clear documentation for adding new providers
  - Show how to leverage the shared utilities
  - Provide examples of following established patterns

- [ ] Fix unused arguments and imports
  - Address ARG002 linter errors in provider classes
  - Address F401 linter errors for unused imports
  - Refactor method signatures to remove unused parameters

- [ ] Update pyproject.toml
  - Move 'per-file-ignores' to 'lint.per-file-ignores' section

## New Providers

### Simple File Hosting Providers

- [ ] Implement Transfer.sh provider
  - Simple HTTP POST API
  - No authentication required
  - Similar to existing simple providers
  - Good for temporary file sharing

- [ ] Implement AnonFiles provider
  - Simple API for anonymous file uploads
  - Returns direct download links
  - No authentication required
  - Similar implementation to existing simple providers

### Cloud Storage Providers

- [ ] Implement Google Drive provider
  - Requires OAuth2 authentication
  - Leverage existing async/sync patterns
  - Add support for folder organization
  - Dependencies: google-api-python-client, google-auth

- [ ] Implement Microsoft OneDrive provider
  - Requires OAuth2 authentication
  - Similar to Dropbox implementation pattern
  - Dependencies: Office365-REST-Python-Client or Microsoft Graph SDK

- [ ] Implement pCloud provider
  - API key based authentication
  - Good for privacy-focused users
  - Dependencies: pcloud-sdk-python

### S3-Compatible Storage

- [ ] Implement Backblaze B2 provider
  - S3-compatible API
  - Can leverage existing S3 provider with custom endpoint
  - Cost-effective storage solution
  - Dependencies: boto3 (already used for S3)

- [ ] Implement DigitalOcean Spaces provider
  - S3-compatible API
  - Can leverage existing S3 provider with custom endpoint
  - Dependencies: boto3 (already used for S3)

### Media and Specialized Providers

- [ ] Implement Imgur provider
  - Specialized for image uploads
  - API key based authentication
  - Add image-specific metadata handling
  - Dependencies: requests

- [ ] Implement Cloudinary provider
  - Media transformation capabilities
  - API key based authentication
  - Support for image/video optimization
  - Dependencies: cloudinary or requests

### Version Control Platforms

- [ ] Implement GitHub Gist provider
  - Good for text file sharing with syntax highlighting
  - OAuth or token-based authentication
  - Implement file size and type constraints
  - Dependencies: PyGithub or requests

- [ ] Implement GitLab Snippet provider
  - Similar to GitHub Gist
  - Support for self-hosted GitLab instances
  - Token-based authentication
  - Dependencies: python-gitlab or requests

### Enterprise and Specialized Services

- [ ] Implement Azure Blob Storage provider
  - Microsoft's object storage solution
  - Similar pattern to S3 provider
  - Dependencies: azure-storage-blob

- [ ] Implement Box provider
  - Enterprise file sharing and collaboration
  - OAuth authentication
  - Dependencies: boxsdk

- [ ] Implement WeTransfer provider
  - Popular service for large file transfers
  - API key based authentication
  - Support for expiring links
  - Dependencies: requests

### Decentralized Storage Options

- [ ] Implement IPFS provider via Pinata or Infura
  - Distributed file system
  - Pin files to IPFS network
  - API key based authentication
  - Dependencies: ipfshttpclient or requests

## Implementation Strategy

- [ ] Update provider preference list in `__init__.py` to include new providers
- [ ] Add environment variable documentation for each new provider
- [ ] Create integration tests for each new provider
- [ ] Update documentation with new provider capabilities and requirements

## Completed Tasks

- [x] Create utils.py to centralize common functionality for upload providers
  
  A `utils.py` file has been created in the `upload_providers` folder with several helper functions:
  - `create_provider_help` for standardizing provider help dictionaries
  - `safe_file_handle` for file operations
  - `validate_file` for file validation
  - `handle_http_response` for HTTP response handling
  - `get_env_credentials` for credential management
  - `create_provider_instance` for provider initialization
  - `standard_upload_wrapper` for consistent upload handling
  - `log_upload_attempt` for consistent logging

- [x] Refactor provider modules to use utils.py consistently
  
  All providers have been refactored:
  - pixeldrain.py, bashupload.py, catbox.py, filebin.py
  - uguu.py, www0x0.py, dropbox.py, s3.py
  - fal.py, litterbox.py

- [x] Create provider templates for standardized implementation
  
  Created two template files in the `templates` directory:
  - `simple_provider_template.py` for providers without authentication
  - `authenticated_provider_template.py` for providers requiring credentials

- [x] Implement a factory pattern for provider instantiation
  
  Created a factory.py module with a ProviderFactory class that:
  - Centralizes provider instantiation logic
  - Standardizes error handling during initialization
  - Reduces code duplication in provider creation
  - Provides a cleaner API for getting provider instances

- [x] Standardize async/sync conversion patterns
  
  Created an async_utils.py module with utilities for async/sync conversion:
  - `run_async` for running coroutines in a synchronous context
  - `to_sync` decorator for converting async functions to sync
  - `to_async` decorator for converting sync functions to async
  - `gather_with_concurrency` for limiting concurrent async operations
  - `AsyncContextManager` base class for implementing async context managers
  - `with_async_timeout` decorator for adding timeouts to async functions

- [x] Write unit tests for utils.py functions
  
  Created comprehensive test files:
  - test_utils.py for testing the utils.py module
  - test_async_utils.py for testing the async_utils.py module
  - Tests cover all utility functions thoroughly
  - Tests include edge cases and error conditions
  - Tests ensure backward compatibility

- [x] Create provider base classes to reduce inheritance boilerplate
  
  Created base classes in simple.py:
  - BaseProvider: Common functionality for all providers
  - AsyncBaseProvider: For providers with native async support
  - SyncBaseProvider: For providers with sync-only implementations