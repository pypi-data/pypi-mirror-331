#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "aiohttp",
#   "fire"
# ]
# ///

import asyncio
import fire
from pathlib import Path
from src.uploaders import get_uploader


async def upload_file(file_path: str, service: str = "bash") -> str:
    """Upload a file using the specified service

    Args:
        file_path: Path to file to upload
        service: Upload service to use ('bash', 'www0x0', 'uguu')

    Returns:
        URL of uploaded file

    Raises:
        ValueError if service is not recognized
    """
    uploader = get_uploader(service)
    result = await uploader.upload_file(Path(file_path))

    if result.success:
        return result.url
    else:
        msg = f"Upload failed: {result.error}"
        raise Exception(msg)


def main(file_path: str, service: str = "bash"):
    """CLI entry point"""
    return asyncio.run(upload_file(file_path, service))


if __name__ == "__main__":
    fire.Fire(main)
