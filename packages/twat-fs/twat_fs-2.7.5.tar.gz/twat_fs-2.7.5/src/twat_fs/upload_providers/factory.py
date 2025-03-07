# this_file: src/twat_fs/upload_providers/factory.py

"""
Factory pattern implementation for provider instantiation.
This module centralizes the creation of providers and standardizes error handling.
"""

from __future__ import annotations

import importlib
from typing import TypeVar, cast, TYPE_CHECKING

from loguru import logger
from twat_cache import ucache

from twat_fs.upload_providers.protocols import Provider, ProviderClient, ProviderHelp

if TYPE_CHECKING:
    from collections.abc import Sequence

# Type variable for provider classes
T = TypeVar("T", bound=Provider)


class ProviderFactory:
    """
    Factory class for creating provider instances.
    Centralizes provider instantiation and error handling.
    """

    @staticmethod
    def get_provider_module(provider_name: str) -> Provider | None:
        """
        Get the provider module for a given provider name.

        Args:
            provider_name: Name of the provider to get

        Returns:
            Optional[Provider]: Provider module if found and properly configured
        """
        return ProviderFactory._get_provider_module_impl(provider_name)

    @staticmethod
    @ucache(maxsize=50)  # Cache up to 50 provider modules
    def _get_provider_module_impl(provider_name: str) -> Provider | None:
        return ProviderFactory._get_provider_module_uncached(provider_name)

    @staticmethod
    def _get_provider_module_uncached(provider_name: str) -> Provider | None:
        """
        Uncached implementation of get_provider_module.
        """
        try:
            # Skip the 'simple' provider as it's just a base class
            if provider_name.lower() == "simple":
                return None

            # Try to import the module
            try:
                module = importlib.import_module(
                    f".{provider_name}", "twat_fs.upload_providers"
                )
            except ImportError as e:
                if "No module named" in str(e):
                    logger.debug(f"Provider module {provider_name} not found")
                else:
                    logger.warning(f"Error importing provider {provider_name}: {e}")
                return None

            # Verify the module implements the Provider protocol
            required_attrs = ["get_provider", "get_credentials", "upload_file"]
            missing_attrs = [
                attr for attr in required_attrs if not hasattr(module, attr)
            ]

            if missing_attrs:
                logger.warning(
                    f"Provider {provider_name} is missing required attributes: {', '.join(missing_attrs)}"
                )
                return None

            # Check for provider help
            if not hasattr(module, "PROVIDER_HELP"):
                logger.warning(f"Provider {provider_name} is missing help information")
                return None

            return cast(Provider, module)

        except Exception as e:
            logger.error(f"Unexpected error loading provider {provider_name}: {e}")
            return None

    @staticmethod
    def get_provider_help(provider_name: str) -> ProviderHelp | None:
        """
        Get help information for a provider.

        Args:
            provider_name: Name of the provider to get help for

        Returns:
            Optional[ProviderHelp]: Help information if provider exists
        """
        try:
            # Skip the 'simple' provider
            if provider_name.lower() == "simple":
                return {
                    "setup": "This is a base provider and should not be used directly.",
                    "deps": "None",
                }

            # Try to get the module
            module = ProviderFactory.get_provider_module(provider_name)
            if module is None:
                # Try to import just for help info
                try:
                    module = importlib.import_module(
                        f".{provider_name}", "twat_fs.upload_providers"
                    )
                    return getattr(module, "PROVIDER_HELP", None)
                except ImportError:
                    return None

            return getattr(module, "PROVIDER_HELP", None)

        except Exception as e:
            logger.error(f"Error getting help for provider {provider_name}: {e}")
            return None

    @staticmethod
    def create_provider(provider_name: str) -> ProviderClient | None:
        """
        Create a provider instance with standardized error handling.

        Args:
            provider_name: Name of the provider to create

        Returns:
            Optional[ProviderClient]: Provider client if successful, None otherwise
        """
        try:
            provider_module = ProviderFactory.get_provider_module(provider_name)
            if provider_module is None:
                logger.warning(f"Provider module {provider_name} not found")
                return None

            # Get credentials and create provider
            provider_module.get_credentials()

            # Use the module's get_provider method
            provider = provider_module.get_provider()

            if provider is None:
                logger.warning(f"Failed to initialize provider {provider_name}")
                return None

            return provider

        except Exception as e:
            logger.error(f"Error creating provider {provider_name}: {e}")
            return None

    @staticmethod
    def create_providers(
        provider_names: Sequence[str],
    ) -> dict[str, ProviderClient | None]:
        """
        Create multiple provider instances.

        Args:
            provider_names: Names of providers to create

        Returns:
            Dict[str, Optional[ProviderClient]]: Dictionary of provider name to provider instance
        """
        providers = {}
        for name in provider_names:
            providers[name] = ProviderFactory.create_provider(name)
        return providers
