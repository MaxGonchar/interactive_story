import pytest

import app.utils.yaml_storage as ys


@pytest.mark.asyncio
async def test_read_yaml_returns_dict(tmp_path):
    data = {"key": "value", "number": 42}
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_bytes(ys.dump_yaml(data))

    result = await ys.read_yaml(yaml_file)

    assert result == data


@pytest.mark.asyncio
async def test_read_yaml_raises_file_not_found(tmp_path):
    missing = tmp_path / "nonexistent.yaml"

    with pytest.raises(FileNotFoundError):
        await ys.read_yaml(missing)


def test_dump_yaml_returns_bytes():
    result = ys.dump_yaml({"a": 1})

    assert isinstance(result, bytes)


@pytest.mark.asyncio
async def test_round_trip_preserves_data(tmp_path):
    original = {"name": "hero", "level": 5, "tags": ["brave", "swift"]}
    yaml_file = tmp_path / "round_trip.yaml"

    yaml_file.write_bytes(ys.dump_yaml(original))
    loaded = await ys.read_yaml(yaml_file)

    loaded["level"] = 6
    yaml_file.write_bytes(ys.dump_yaml(loaded))
    final = await ys.read_yaml(yaml_file)

    assert final["name"] == "hero"
    assert final["level"] == 6
    assert final["tags"] == ["brave", "swift"]
