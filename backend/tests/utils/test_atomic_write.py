from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

import app.utils.atomic_write as aw


@pytest.mark.asyncio
async def test_creates_file(tmp_path):
    target = tmp_path / "output.yaml"
    data = b"key: value\n"

    await aw.atomic_write(target, data)

    assert target.read_bytes() == data


@pytest.mark.asyncio
async def test_no_tmp_file_remains(tmp_path):
    target = tmp_path / "output.yaml"

    await aw.atomic_write(target, b"data: 1\n")

    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()


@pytest.mark.asyncio
async def test_overwrites_existing(tmp_path):
    target = tmp_path / "output.yaml"
    target.write_bytes(b"old: true\n")

    await aw.atomic_write(target, b"new: true\n")

    assert target.read_bytes() == b"new: true\n"


@pytest.mark.asyncio
async def test_creates_parent_dirs(tmp_path):
    target = tmp_path / "a" / "b" / "c" / "output.yaml"
    data = b"nested: true\n"

    await aw.atomic_write(target, data)

    assert target.read_bytes() == data


@pytest.mark.asyncio
async def test_cleans_up_tmp_on_exception(tmp_path):
    target = tmp_path / "output.yaml"
    original_data = b"original: true\n"
    target.write_bytes(original_data)

    with patch("os.replace", side_effect=OSError("rename failed")):
        with pytest.raises(OSError, match="rename failed"):
            await aw.atomic_write(target, b"new: true\n")

    tmp = target.with_suffix(target.suffix + ".tmp")
    assert not tmp.exists()
    assert target.read_bytes() == original_data
