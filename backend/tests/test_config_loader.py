from __future__ import annotations

from app.config.loader import ConfigLoader
from app.config.validator import ConfigValidator


def test_config_loader_writes_and_rolls_back_invalid_config(tmp_path) -> None:
    config_root = tmp_path / "config"
    config_root.mkdir()
    path = config_root / "app.yaml"
    path.write_text("version: 1\nname: ok\n", encoding="utf-8")
    loader = ConfigLoader(config_root)

    loader.write("app.yaml", {"version": 1, "name": "updated"})
    assert loader.read("app.yaml")["name"] == "updated"
    assert loader.rollback("app.yaml")["ok"]
    assert loader.read("app.yaml")["name"] == "ok"
    loader.write("app.yaml", {"version": 1, "name": "updated"})

    try:
        loader.write("app.yaml", {"name": "missing-version"})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid config write should fail")

    assert loader.read("app.yaml")["name"] == "updated"


def test_config_validator_rejects_invalid_provider_shape(tmp_path) -> None:
    provider_dir = tmp_path / "config" / "providers"
    provider_dir.mkdir(parents=True)
    path = provider_dir / "custom.yaml"
    path.write_text(
        """
version: 1
name: custom
provider_type: custom
enabled: "yes"
base_url: not-a-url
model_profiles:
  fast: 123
""",
        encoding="utf-8",
    )

    result = ConfigValidator().validate_file(path)

    assert result.ok is False
    assert "enabled must be a boolean" in result.errors
    assert "base_url must be an http(s) URL" in result.errors
    assert "model_profiles.fast must be a string" in result.errors


def test_config_loader_rejects_invalid_tool_shape(tmp_path) -> None:
    tool_dir = tmp_path / "config" / "tools"
    tool_dir.mkdir(parents=True)
    path = tool_dir / "demo.yaml"
    path.write_text("version: 1\nname: demo\ntimeout_seconds: 5\n", encoding="utf-8")
    loader = ConfigLoader(tmp_path / "config")

    try:
        loader.write("tools/demo.yaml", {"version": 1, "name": "demo", "timeout_seconds": -1})
    except ValueError as exc:
        assert "timeout_seconds must be a positive number" in str(exc)
    else:
        raise AssertionError("invalid tool config write should fail")
