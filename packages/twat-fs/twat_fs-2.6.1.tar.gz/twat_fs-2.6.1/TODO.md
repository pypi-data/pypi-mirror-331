---
this_file: TODO.md
---

# TODO

Tip: Periodically run `python ./cleanup.py status` to see results of lints and tests. Use `uv pip ...` not `pip ...`

## High Priority

- [ ] Fix missing dependencies for tests
  - [ ] Install missing dependencies for tests or implement proper test skipping
    - Issue: ModuleNotFoundError for 'fal_client', 'botocore', 'responses'
    - Fix: Add `uv pip install 'twat-fs[test,dev]'` or implement conditional imports with proper test skipping
    - Affected files:
      - `tests/test_integration.py`: Needs 'fal_client'
      - `tests/test_s3_advanced.py`: Needs 'botocore'
      - `tests/test_upload.py`: Needs 'botocore'

- [ ] Fix failing unit tests
  - [ ] Fix `TestLogUploadAttempt.test_log_upload_attempt_success` test
    - Issue: logger.info is not being called in the log_upload_attempt function
    - Fix: Implement proper logger.info call in the success branch
  - [ ] Fix `TestGatherWithConcurrency.test_gather_with_concurrency_with_exceptions` test
    - Issue: Test is failing with RuntimeError instead of ValueError
    - Fix: Ensure the correct exception type is propagated in gather_with_concurrency

- [ ] Fix boolean argument issues
  - [ ] Fix FBT001/FBT002 linter errors for boolean positional arguments
    - Issue: Boolean-typed positional arguments in function definitions
    - Fix: Convert boolean positional arguments to keyword-only arguments
    - Affected files:
      - `utils.py` line 251: `log_upload_attempt` function
      - `upload.py` lines 251, 381: `setup_provider` and `setup_providers` functions
      - `cli.py` lines 202, 203, 205: `upload` method
  - [ ] Fix FBT003 linter errors for boolean positional values in function calls
    - Affected files:
      - `upload.py` multiple instances in `ProviderInfo` instantiation
      - `test_utils.py` lines 340, 349: `log_upload_attempt` calls

- [ ] Fix type annotation issues
  - [ ] Fix incompatible return types in async methods
    - Issue: Return type mismatches in async functions
    - Affected files:
      - `simple.py` lines 120, 156, 273: Return type incompatibilities
  - [ ] Fix type mismatches in factory.py
    - Issue: Incompatible types in assignment (expression has type Module, variable has type "Provider | None")
  - [ ] Fix missing type annotations
    - Issue: Need type annotation for variables
    - Affected files:
      - `simple.py` lines 237, 261: Missing type annotations for "sync_upload"

## Medium Priority

- [ ] Fix exception handling issues
  - [ ] Fix B904 linter errors (raise with from)
    - Issue: Within an `except` clause, raise exceptions with `raise ... from err`
    - Affected files:
      - `upload.py` line 687
      - `fal.py` line 67
  - [ ] Fix S101 linter errors (use of assert)
    - Affected files:
      - `core.py` lines 168, 214

- [ ] Fix unused arguments and imports
  - [ ] Fix ARG002 linter errors (unused method arguments)
    - Affected files:
      - `dropbox.py` line 124: Unused `kwargs`
      - `s3.py` line 182: Unused `kwargs`
      - `simple.py` multiple instances: Unused arguments
  - [ ] Fix F401 linter errors (unused imports)
    - Affected files:
      - `__init__.py` lines 11, 19: Unused imports

- [ ] Fix function complexity issues
  - [ ] Refactor functions with too many arguments (PLR0913)
    - Affected files:
      - `cli.py` line 198: `upload` method
      - `upload.py` lines 411, 550, 619, 703: Multiple functions
      - `litterbox.py` lines 223, 300: `upload_file` functions
  - [ ] Refactor complex functions (C901)
    - Affected files:
      - `upload.py` lines 57, 250: `_test_provider_online` and `setup_provider` functions
  - [ ] Fix functions with too many branches/statements/returns (PLR0911, PLR0912, PLR0915)
    - Affected files:
      - `upload.py` lines 57, 250: Multiple complexity issues

## Low Priority

- [ ] Fix linter issues in `cleanup.py`
  - [ ] Address DTZ005: datetime.datetime.now() called without a tz argument
  - [ ] Fix S603/S607: Subprocess call security issues

- [ ] Update `pyproject.toml` to fix deprecated linter settings
  - [ ] Update ruff configuration
  - [ ] Add explicit Python version targets
  - [ ] Configure mypy settings

- [ ] Fix RUF012 linter errors (mutable class attributes)
  - Affected files:
    - `fal.py` lines 51, 52: Mutable class attributes should be annotated with `typing.ClassVar`

- [ ] Fix A005 linter error (module shadows standard library)
  - Affected files:
    - `types.py` line 1: Module `types` shadows a Python standard-library module

- [ ] Fix S105 linter error (possible hardcoded password)
  - Affected files:
    - `test_s3_advanced.py` line 21: Hardcoded "TEST_SECRET_KEY"

## Documentation

- [ ] Document best practices for creating new providers
  - [ ] Create comprehensive provider development guide
  - [ ] Add examples for common provider patterns

- [ ] Update API documentation with latest changes

- [ ] Create troubleshooting guide for common issues

## New Providers

- [ ] Add support for Imgur
- [ ] Add support for Cloudinary
- [ ] Add support for Google Drive
- [ ] Add support for OneDrive
- [ ] Add support for Box
- [ ] Add support for Mega
- [ ] Add support for Backblaze B2
- [ ] Add support for Wasabi

## Completed Tasks

- [x] Fix `TestCreateProviderInstance` tests
- [x] Fix `TestGatherWithConcurrency` tests
- [x] Create `utils.py` module for shared functionality
- [x] Refactor provider modules to use `utils.py`
- [x] Create provider templates
- [x] Implement factory pattern for provider instantiation
- [x] Standardize async/sync conversion patterns
- [x] Write unit tests for utility functions
- [x] Create provider base classes
- [x] Improve error classification with `RetryableError` and `NonRetryableError` classes
- [x] Standardize logging patterns with `log_upload_attempt` function
- [x] Enhance type hints for better IDE support and runtime type checking
- [x] Improve URL validation to ensure returned URLs are accessible before returning them

