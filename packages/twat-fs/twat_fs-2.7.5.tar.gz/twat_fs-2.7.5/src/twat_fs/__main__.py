#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "fire",
# ]
# ///
# this_file: src/twat_fs/__main__.py

"""
Command-line interface for twat-fs package.

Usage:
    twat-fs upload FILE [--provider PROVIDER]
    twat-fs setup provider PROVIDER
    twat-fs setup all

Commands:
    upload      Upload a file using the specified provider
    setup       Check provider setup and configuration

Examples:
    # Upload a file using default provider
    twat-fs upload path/to/file.txt

    # Upload using specific provider
    twat-fs upload path/to/file.txt --provider s3

    # Check provider setup
    twat-fs setup provider s3
    twat-fs setup all
"""

from twat_fs.cli import main

if __name__ == "__main__":
    main()
