from __future__ import annotations

from app.config.loader import ConfigLoader


def test_config_loader_writes_and_rolls_back_invalid_config(tmp_path) -> None:
    config_root = tmp_path / "config"
    config_root.mkdir()
    path = config_root / "app.yaml"
    path.write_text("version: 1\nname: ok\n", encoding="utf-8")
    loader = ConfigLoader(config_root)

    loader.write("app.yaml", {"version": 1, "name": "updated"})
    assert loader.read("app.yaml")["name"] == "updated"

    try:
        loader.write("app.yaml", {"name": "missing-version"})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid config write should fail")

    assert loader.read("app.yaml")["name"] == "updated"
