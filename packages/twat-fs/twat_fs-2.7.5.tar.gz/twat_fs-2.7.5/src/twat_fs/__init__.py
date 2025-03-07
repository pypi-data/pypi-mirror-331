# this_file: src/twat_fs/__init__.py

"""
twat-fs package - File system utilities for twat.
"""

from importlib import metadata

try:
    import twat_cache
    from twat_fs.paths import get_cache_dir

    # Configure twat_cache to use the paths from twat_os
    # Use the correct API to set the cache directory
    twat_cache.utils.get_cache_path = lambda *args, **kwargs: get_cache_dir()
except ImportError:
    pass  # twat_cache is not installed, no configuration needed

from twat_fs.cli import main, setup_provider, setup_providers, upload_file
from twat_fs.upload import PROVIDERS_PREFERENCE, ProviderType

__version__ = metadata.version(__name__)

__all__ = [
    "PROVIDERS_PREFERENCE",
    "ProviderType",
    "main",
    "setup_provider",
    "setup_providers",
    "upload_file",
]
