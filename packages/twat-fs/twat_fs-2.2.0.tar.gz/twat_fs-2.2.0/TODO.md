---
this_file: TODO.md
---

# TODO

## 1. Refactoring

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

- [ ] Refactor provider modules to use utils.py consistently
  
  Progress:
  - [x] pixeldrain.py has been refactored to use utils.py functions
    - Fixed recursion issue in `get_provider` method
    - Improved error handling with proper exception chaining
    - Extracted response processing to a separate method
    - Implemented manual retry logic with exponential backoff
    - Reduced complexity and improved code quality
    - Standardized logging with `log_upload_attempt`
    - Improved HTTP response handling with `handle_http_response`
  - [x] bashupload.py has been refactored to use utils.py functions
    - Implemented consistent error handling with RetryableError and NonRetryableError
    - Added standardized logging with log_upload_attempt
    - Improved HTTP response handling with handle_http_response
    - Simplified upload_file method using standard_upload_wrapper
  - [x] catbox.py has been refactored to use utils.py functions
    - Separated upload logic into _do_upload method
    - Standardized provider help format with create_provider_help
    - Added proper error handling and logging
    - Simplified module-level functions
  - [x] filebin.py has been refactored to use utils.py functions
    - Improved error handling with handle_http_response
    - Added standardized logging with log_upload_attempt
    - Simplified upload_file method using standard_upload_wrapper
  - [x] uguu.py has been refactored to use utils.py functions
    - Separated upload logic into _do_upload method
    - Standardized provider help format with create_provider_help
    - Added proper error handling and logging
    - Simplified module-level functions
  - [x] www0x0.py has been refactored to use utils.py functions
    - Separated upload logic into _do_upload method
    - Standardized provider help format with create_provider_help
    - Added proper error handling and logging
    - Simplified module-level functions
  - [x] dropbox.py has been refactored to use utils.py functions
    - Made DropboxClient inherit from BaseProvider
    - Standardized provider help format with create_provider_help
    - Added proper credential handling with get_env_credentials
    - Improved file validation with validate_file
    - Added standardized logging with log_upload_attempt
    - Separated upload logic into upload_file_impl method
    - Fixed method signatures to match BaseProvider interface
  - [x] s3.py has been refactored to use utils.py functions
    - Created S3Provider class inheriting from BaseProvider
    - Standardized provider help format with create_provider_help
    - Added proper credential handling with get_env_credentials
    - Improved error handling with RetryableError and NonRetryableError
    - Added standardized logging with log_upload_attempt
    - Separated upload logic into _do_upload and upload_file_impl methods
    - Simplified upload_file method using standard_upload_wrapper
  
  Remaining providers to refactor:
  - [ ] fal.py
  - [ ] litterbox.py

  The priority is to:
  1. Replace duplicated code with calls to utils.py functions
  2. Ensure consistent error handling across providers
  3. Standardize method signatures and patterns

- [x] Create provider templates for standardized implementation
  
  Created two template files in the `templates` directory:
  - `simple_provider_template.py` for providers without authentication
  - `authenticated_provider_template.py` for providers requiring credentials
  
  These templates include:
  - Standard imports and class structure
  - Consistent error handling patterns
  - Proper use of utility functions from utils.py
  - Documentation templates and type annotations
  - Module-level functions implementing the Provider protocol

- [ ] Implement a factory pattern for provider instantiation
  
  Create a provider factory that simplifies the creation of providers and reduces code duplication in `get_provider()` methods.

- [ ] Standardize async/sync conversion patterns
  
  Several providers implement both synchronous and asynchronous upload methods with nearly identical conversion logic. Standardize this pattern using the utilities in utils.py.

- [ ] Refine HTTP response handling across providers
  
  While `handle_http_response()` exists in utils.py, ensure all providers use it consistently for handling various HTTP status codes, especially for error conditions like rate limits (429) and other non-200 responses.

- [ ] Create provider base classes to reduce inheritance boilerplate
  
  Implement base classes that providers can inherit from to reduce duplicate code:
  - A base class for simple providers with no credentials
  - A base class for async-capable providers
  - A base class for providers requiring credentials

- [ ] Add comprehensive type annotations for async operations
  
  With the protocol updates to support both `Awaitable[UploadResult]` and `Coroutine[Any, Any, UploadResult]`, ensure consistent type handling in:
  - Async/await conversions
  - Async decorators with proper type hints
  - Async context managers and resource cleanup

- [ ] Write unit tests for utils.py functions
  
  Ensure the centralized utilities are thoroughly tested to prevent regressions when refactoring providers.

- [ ] Document best practices for creating new providers
  
  Create clear documentation for adding new providers, showing how to leverage the shared utilities and follow the established patterns.

## 2. Implement Additional Upload Providers

Based on the analysis of feasible ideas from IDEAS.md:

### 2.1. Simple File Hosting Providers

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

### 2.2. Cloud Storage Providers

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

### 2.3. S3-Compatible Storage

- [ ] Implement Backblaze B2 provider
  - S3-compatible API
  - Can leverage existing S3 provider with custom endpoint
  - Cost-effective storage solution
  - Dependencies: boto3 (already used for S3)

- [ ] Implement DigitalOcean Spaces provider
  - S3-compatible API
  - Can leverage existing S3 provider with custom endpoint
  - Dependencies: boto3 (already used for S3)

### 2.4. Media and Specialized Providers

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

### 2.5. Version Control Platforms

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

### 2.6. Enterprise and Specialized Services

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

### 2.7. Decentralized Storage Options

- [ ] Implement IPFS provider via Pinata or Infura
  - Distributed file system
  - Pin files to IPFS network
  - API key based authentication
  - Dependencies: ipfshttpclient or requests

### 2.8. Implementation Strategy

- [ ] Create a template provider module to standardize implementation
  - Include required imports
  - Standard method implementations
  - Common error handling patterns
  - Documentation template

- [ ] Update provider preference list in `__init__.py` to include new providers

- [ ] Add environment variable documentation for each new provider

- [ ] Create integration tests for each new provider

- [ ] Update documentation with new provider capabilities and requirements