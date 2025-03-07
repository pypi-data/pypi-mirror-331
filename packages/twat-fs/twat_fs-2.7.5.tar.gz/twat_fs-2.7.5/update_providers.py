#!/usr/bin/env python3

import re
from pathlib import Path


def update_provider_file(file_path: Path) -> None:
    """Update a provider file to use BaseProvider and standardize upload methods."""
    with open(file_path) as f:
        content = f.read()

    # Replace SimpleProviderBase with BaseProvider
    content = content.replace("SimpleProviderBase", "BaseProvider")

    # Update imports
    content = content.replace(
        "from twat_fs.upload_providers.simple import SimpleProviderBase, UploadResult",
        "from twat_fs.upload_providers.types import UploadResult\nfrom twat_fs.upload_providers.simple import BaseProvider",
    )

    content = content.replace(
        "from twat_fs.upload_providers.simple import BaseProvider, UploadResult",
        "from twat_fs.upload_providers.types import UploadResult\nfrom twat_fs.upload_providers.simple import BaseProvider",
    )

    # Add convert_to_upload_result import
    if "from twat_fs.upload_providers.core import" in content:
        content = content.replace(
            "from twat_fs.upload_providers.core import",
            "from twat_fs.upload_providers.core import convert_to_upload_result, ",
        )
    else:
        content = content.replace(
            "from twat_fs.upload_providers.protocols import",
            "from twat_fs.upload_providers.core import convert_to_upload_result\n\nfrom twat_fs.upload_providers.protocols import",
        )

    # Update module-level upload_file function to return UploadResult
    def replace_upload_file(match):
        signature = match.group(1)
        return f"def upload_file{signature} -> UploadResult:"

    content = re.sub(
        r"def upload_file\((.*?)\) -> str:",
        replace_upload_file,
        content,
        flags=re.DOTALL,
    )

    # Update function body to return UploadResult
    def replace_upload_file_body(match):
        match.group(1)
        return """{
    provider = get_provider()
    if not provider:
        msg = "Failed to initialize provider"
        raise ValueError(msg)
    return provider.upload_file(local_path, remote_path)"""

    content = re.sub(
        r"def upload_file\(.*?\) -> UploadResult:(.*?)return provider\.upload_file\(local_path, remote_path\)",
        replace_upload_file_body,
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w") as f:
        f.write(content)


def main():
    providers = [
        "www0x0.py",
        "catbox.py",
        "dropbox.py",
        "filebin.py",
        "bashupload.py",
        "s3.py",
        "fal.py",
        "pixeldrain.py",
        "litterbox.py",
        "uguu.py",
    ]

    base_path = Path("src/twat_fs/upload_providers")

    for provider in providers:
        file_path = base_path / provider
        update_provider_file(file_path)


if __name__ == "__main__":
    main()
