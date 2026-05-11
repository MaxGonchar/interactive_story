from pathlib import Path

import aiofiles
import yaml


async def read_yaml(path: Path) -> dict:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        content = await f.read()
    return yaml.safe_load(content)


def dump_yaml(data: dict) -> bytes:
    return yaml.safe_dump(data, allow_unicode=True).encode("utf-8")
