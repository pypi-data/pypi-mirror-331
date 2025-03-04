# this_file: src/twat_fs/__init__.py

"""
twat-fs package - File system utilities for twat.
"""

from importlib import metadata

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
