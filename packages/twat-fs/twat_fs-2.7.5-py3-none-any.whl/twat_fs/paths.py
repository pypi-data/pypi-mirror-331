#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["twat-os"]
# ///
# this_file: src/twat_fs/paths.py

"""
Path management for twat-fs.

This module provides standardized paths for cache directories, configuration files,
and any data storage using twat-os.
"""

from pathlib import Path
from typing import Optional

try:
    from twat_os.paths import PathManager
except ImportError:
    PathManager = None


def get_path_manager() -> Optional["PathManager"]:
    """
    Get a PathManager instance for twat-fs.

    Returns:
        Optional[PathManager]: A PathManager instance if twat-os is installed, None otherwise
    """
    if PathManager is None:
        return None

    return PathManager.for_package("twat_fs")


def get_cache_dir() -> Path:
    """
    Get the cache directory for twat-fs.

    Returns:
        Path: The cache directory path
    """
    path_manager = get_path_manager()
    if path_manager:
        return path_manager.cache.base_dir

    # Fallback to a default path if twat-os is not installed
    import platformdirs

    return Path(platformdirs.user_cache_dir()) / "twat" / "fs"


def get_config_dir() -> Path:
    """
    Get the configuration directory for twat-fs.

    Returns:
        Path: The configuration directory path
    """
    path_manager = get_path_manager()
    if path_manager:
        return path_manager.config.base_dir

    # Fallback to a default path if twat-os is not installed
    import platformdirs

    return Path(platformdirs.user_config_dir()) / "twat" / "fs"


def get_data_dir() -> Path:
    """
    Get the data directory for twat-fs.

    Returns:
        Path: The data directory path
    """
    path_manager = get_path_manager()
    if path_manager:
        return path_manager.data.base_dir

    # Fallback to a default path if twat-os is not installed
    import platformdirs

    return Path(platformdirs.user_data_dir()) / "twat" / "fs"
