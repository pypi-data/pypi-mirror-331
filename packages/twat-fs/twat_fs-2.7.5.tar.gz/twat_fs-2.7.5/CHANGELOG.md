---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Provider templates for standardized implementation:
  - `simple_provider_template.py`: Template for providers without authentication
  - `authenticated_provider_template.py`: Template for providers requiring credentials
- Factory pattern for provider instantiation to simplify provider creation and standardize error handling
- Comprehensive unit tests for utility functions
- Base classes for providers to reduce inheritance boilerplate
- Standardized logging patterns with `log_upload_attempt` function
- Improved error classification with `RetryableError` and `NonRetryableError` classes
- Centralized utilities in `utils.py` module for shared functionality across providers
- URL validation to ensure returned URLs are accessible before returning them
- Standardized async/sync conversion patterns with `to_sync` and `to_async` decorators

### Changed
- Fixed `create_provider_instance` function in `utils.py` to correctly handle credential management
- Fixed `gather_with_concurrency` function in `async_utils.py` to properly handle coroutines
- Refactored all upload providers to use shared utilities from `utils.py`:
  - `pixeldrain.py`: Fixed recursion issues, improved error handling, standardized logging
  - `bashupload.py`: Implemented consistent error handling, standardized logging
  - `catbox.py`: Separated upload logic, standardized provider help format
  - `filebin.py`: Improved error handling, standardized logging
  - `uguu.py`: Separated upload logic, standardized provider help format
  - `www0x0.py`: Separated upload logic, standardized provider help format
  - `dropbox.py`: Made DropboxClient inherit from BaseProvider, standardized provider help format
  - `s3.py`: Created S3Provider class inheriting from BaseProvider, improved error handling
  - `fal.py`: Made FalProvider inherit from BaseProvider, improved error handling and credential management
  - `litterbox.py`: Made LitterboxProvider inherit from BaseProvider, improved error handling with special handling for expiration parameter
- Standardized async/sync conversion patterns for providers that support both operations
- Enhanced type hints for better IDE support and runtime type checking
- Improved URL validation to ensure returned URLs are accessible before returning them

### Fixed
- Fixed test failures in `TestCreateProviderInstance` test class
- Fixed test failures in `TestGatherWithConcurrency` test class
- Improved error handling and logging across all providers
- Fixed recursion issues in pixeldrain provider
- Standardized provider help format for better consistency

## In Progress

- Fixing type annotation issues identified by linter
  - Addressing incompatible return types in async methods
  - Fixing type mismatches in factory.py and simple.py
  - Ensuring proper typing for async/await conversions
  - Resolving "possibly unbound" variable warnings in upload.py

- Fixing remaining failing unit tests
  - TestLogUploadAttempt.test_log_upload_attempt_success test failing because logger.info is not being called
  - TestGatherWithConcurrency.test_gather_with_concurrency_with_exceptions test failing with RuntimeError instead of ValueError

- Addressing boolean argument issues
  - Converting boolean positional arguments to keyword-only arguments
  - Fixing FBT001/FBT002 linter errors in function definitions
  - Fixing FBT003 linter errors in function calls

- Addressing linter issues in cleanup.py
  - DTZ005: datetime.datetime.now() called without a tz argument
  - S603/S607: Subprocess call security issues

## Development Log

### Completed

- Fixed `create_provider_instance` function in `utils.py` to correctly handle credential management:
  - Properly calls `get_credentials` when no credentials are provided
  - Ensures correct order of operations for provider instantiation
  - Fixed test failures in `TestCreateProviderInstance` test class
  - Improved error handling and logging

- Refactored all upload providers to use shared utilities from `utils.py`:
  - `pixeldrain.py`: Fixed recursion issues, improved error handling, standardized logging
  - `bashupload.py`: Implemented consistent error handling, standardized logging
  - `catbox.py`: Separated upload logic, standardized provider help format
  - `filebin.py`: Improved error handling, standardized logging
  - `uguu.py`: Separated upload logic, standardized provider help format
  - `www0x0.py`: Separated upload logic, standardized provider help format
  - `dropbox.py`: Made DropboxClient inherit from BaseProvider, standardized provider help format
  - `s3.py`: Created S3Provider class inheriting from BaseProvider, improved error handling
  - `fal.py`: Made FalProvider inherit from BaseProvider, improved error handling and credential management
  - `litterbox.py`: Made LitterboxProvider inherit from BaseProvider, improved error handling with special handling for expiration parameter

- Created provider templates for standardized implementation:
  - `simple_provider_template.py`: Template for providers without authentication
  - `authenticated_provider_template.py`: Template for providers requiring credentials

- Updated `catbox.py` and `bashupload.py` to properly implement both `Provider` and `ProviderClient` protocols
  - Improved error handling with `RetryableError` and `NonRetryableError`
  - Added standardized logging with `log_upload_attempt`
  - Enhanced type hints for better IDE support

- Implemented a factory pattern for provider instantiation to simplify provider creation and standardize error handling during initialization

- Standardized async/sync conversion patterns for providers that support both operations

- Created comprehensive unit tests for utility functions

### Next Steps

- Fix missing dependencies for tests
  - Install missing dependencies for tests or implement proper test skipping
  - Address ModuleNotFoundError for 'responses', 'fal_client', 'botocore'

- Fix boolean argument issues
  - Convert boolean positional arguments to keyword-only arguments
  - Fix FBT001/FBT002 linter errors in function definitions
  - Fix FBT003 linter errors in function calls

- Fix type annotation issues
  - Address incompatible return types in async methods
  - Fix type mismatches in factory.py and simple.py
  - Add missing type annotations for variables

- Fix exception handling issues
  - Implement proper exception chaining with `raise ... from err`
  - Replace assert statements with proper error handling

- Fix function complexity issues
  - Refactor functions with too many arguments
  - Simplify complex functions with too many branches/statements/returns

### Technical Debt

- Update provider implementations to match new protocol type hints
- Standardize error handling across all providers
- Improve documentation for adding new providers
- Fix linter warnings related to boolean arguments and function complexity
- Refactor complex functions in cli.py and upload.py

