#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fire", "loguru", "rich"]
# ///
# this_file: src/twat_fs/cli.py

"""
Command-line interface for twat-fs package.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import fire
from loguru import logger
from rich.console import Console

from twat_fs.upload import (
    PROVIDERS_PREFERENCE,
    setup_provider as _setup_provider,
    setup_providers as _setup_providers,
    upload_file as _upload_file,
)

# Configure logging: errors and warnings to stderr, provider info to stdout
logger.remove()  # Remove default handler
log_level = os.getenv("LOGURU_LEVEL", "INFO").upper()

# All warnings and errors go to stderr
logger.add(
    sys.stderr,
    level="WARNING",
    format="<red>Error: {message}</red>",
)

# Info and debug messages go to stdout, but only for non-error records
logger.add(
    sys.stdout,
    level=log_level,
    format="{message}",
    filter=lambda record: record["level"].no < logger.level("WARNING").no,
)


def parse_provider_list(provider: str) -> list[str] | None:
    """Parse a provider list string like '[s3,dropbox]' into a list."""
    if provider.startswith("[") and provider.endswith("]"):
        try:
            return [p.strip() for p in provider[1:-1].split(",")]
        except Exception:
            return None
    return None


class UploadProviderCommands:
    """Commands for managing upload providers."""

    def status(self, provider_id: str | None = None, online: bool = False) -> None:
        """
        Show provider setup status.

        Args:
            provider_id: Optional provider ID to show status info for.
            online: If True, run online tests to verify provider functionality.
        """
        console = Console(stderr=True)  # Use stderr for error messages

        if provider_id:
            with console.status("[cyan]Testing provider...[/cyan]"):
                result = _setup_provider(provider_id, verbose=True, online=online)
                if result.success:
                    console.print(
                        f"\n[green]Provider {provider_id} is ready to use[/green]"
                    )
                    if online and result.timing:
                        console.print(
                            f"\n[cyan]Online test time: {result.timing.get('total_duration', 0.0):.2f}s[/cyan]"
                        )
                else:
                    console.print(f"\n[red]Provider {provider_id} is not ready[/red]")
                    console.print(f"\n[yellow]Reason:[/yellow] {result.explanation}")
                    console.print("\n[yellow]Setup Instructions:[/yellow]")
                    console.print(
                        result.help_info.get("setup", "No setup instructions available")
                    )
        else:
            from rich.table import Table

            table = Table(title="Provider Setup Status", show_lines=True)
            table.add_column("Provider", no_wrap=True)
            table.add_column("Status", no_wrap=True)
            if online:
                table.add_column("Time (s)", justify="right", no_wrap=True)
            table.add_column("Details", width=50)

            with console.status("[cyan]Testing providers...[/cyan]") as status:
                results = _setup_providers(verbose=True, online=online)

                # Sort providers: Ready first (by time), then Not Ready (alphabetically)
                sorted_providers = []
                ready_providers = []
                not_ready_providers = []

                for provider, info in results.items():
                    if provider.lower() == "simple":
                        continue  # Skip the base provider

                    if info.success:
                        time = (
                            info.timing.get("total_duration", float("inf"))
                            if info.timing
                            else float("inf")
                        )
                        ready_providers.append((provider, info, time))
                    else:
                        time = (
                            info.timing.get("total_duration", float("inf"))
                            if info.timing
                            else float("inf")
                        )
                        not_ready_providers.append((provider, info, time))

                # Sort ready providers by time
                ready_providers.sort(key=lambda x: x[2])
                # Sort not ready providers alphabetically
                not_ready_providers.sort(key=lambda x: x[0])

                # Combine sorted lists
                sorted_providers = [(p, i) for p, i, _ in ready_providers] + [
                    (p, i) for p, i, _ in not_ready_providers
                ]

                for provider, info in sorted_providers:
                    status = (
                        "[green]Ready[/green]"
                        if info.success
                        else "[red]Not Ready[/red]"
                    )
                    details = info.explanation
                    if info.help_info.get("setup"):
                        details = f"{details}\n{info.help_info['setup']}"

                    if online:
                        time = ""
                        if (
                            info.timing
                            and info.timing.get("total_duration") is not None
                        ):
                            time = f"{info.timing.get('total_duration', 0.0):.2f}"
                        row = [provider, status, time, details]
                    else:
                        row = [provider, status, details]

                    table.add_row(*row)

            console.print("\n")  # Add some spacing
            console.print(table)

    def list(self, online: bool = False) -> None:
        """List all available (ready) provider IDs, one per line. If --online is provided, run online tests.
        In online mode, reconfigure logger so that info messages are printed to stderr."""
        if online:
            # Reconfigure logger to send all info messages to stderr
            logger.remove()
            logger.add(sys.stderr, level="INFO", format="{message}")

        active_providers = []

        for provider in PROVIDERS_PREFERENCE:
            if provider.lower() == "simple":
                continue  # Skip the base provider
            result = _setup_provider(provider, verbose=False, online=online)
            if result.success:
                active_providers.append(provider)

        # Print each active provider ID, one per line, to stdout
        for provider in active_providers:
            pass

        sys.exit(0)


class TwatFS:
    """
    A robust and extensible file upload utility with support for multiple storage providers.

    Commands:
        upload              Upload a file using configured providers
        upload_provider    Manage upload providers (status, list)
    """

    def __init__(self) -> None:
        self.upload_provider = UploadProviderCommands()

    def upload(
        self,
        file_path: str | Path,
        provider: str | list[str] = PROVIDERS_PREFERENCE,
        unique: bool = False,
        force: bool = False,
        remote_path: str | None = None,
        fragile: bool = False,
    ) -> str:
        """
        Upload a file using the specified provider(s) with automatic fallback.

        Args:
            file_path: Path to the file to upload
            provider: Provider(s) to use for upload. Can be a single provider or a list
            unique: Add timestamp to filename to ensure uniqueness
            force: Overwrite existing files if they exist
            remote_path: Custom remote path/prefix (provider-specific)
            fragile: If True, fail immediately without trying fallback providers

        Returns:
            URL of the uploaded file
        """
        try:
            # Handle provider list passed as string
            if isinstance(provider, str):
                providers = parse_provider_list(provider)
                if providers is not None:
                    provider = providers

            # Verify file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                sys.exit(1)

            return _upload_file(
                file_path,
                provider=provider,
                unique=unique,
                force=force,
                upload_path=remote_path,
                fragile=fragile,
            )
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    if __name__ == "__main__":
        fire.Fire(TwatFS)
    else:
        # When imported as a module
        fire.Fire(TwatFS())


# Backwards compatibility for the API
upload_file = TwatFS().upload
setup_provider = TwatFS().upload_provider.status


def setup_providers():
    return TwatFS().upload_provider.status(None)


if __name__ == "__main__":
    main()
