import os
from pathlib import Path

import aiofiles


async def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(data)
            await f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
