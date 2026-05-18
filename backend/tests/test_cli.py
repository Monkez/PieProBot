from __future__ import annotations

from pathlib import Path

import argparse

from piepro.cli import DEFAULT_PROJECT_ROOT, build_autostart_command, build_hidden_vbs, build_parser, port_from_url, resolve_root


def test_cli_parser_supports_process_commands() -> None:
    parser = build_parser()
    assert parser.parse_args(["start"]).command == "start"
    assert parser.parse_args(["restart"]).command == "restart"
    assert parser.parse_args(["status"]).command == "status"
    init_args = parser.parse_args(["init"])
    assert init_args.command == "init"
    assert init_args.path is None
    assert parser.parse_args(["init", "PieProBot"]).path == "PieProBot"
    assert parser.parse_args(["use", "."]).command == "use"
    autostart_args = parser.parse_args(["autostart", "enable", "--open"])
    assert autostart_args.command == "autostart"
    assert autostart_args.autostart_command == "enable"
    assert autostart_args.open is True
    assert parser.parse_args(["start", "--no-open"]).no_open is True
    assert DEFAULT_PROJECT_ROOT.name == ".piepro"


def test_cli_resolves_project_root(tmp_path: Path) -> None:
    (tmp_path / "backend" / "app").mkdir(parents=True)
    (tmp_path / "backend" / "app" / "main.py").write_text("", encoding="utf-8")
    (tmp_path / "config").mkdir()
    assert resolve_root(str(tmp_path)) == tmp_path.resolve()


def test_cli_parses_ports_from_urls() -> None:
    assert port_from_url("http://127.0.0.1:8000") == 8000
    assert port_from_url("http://127.0.0.1:3000/dashboard") == 3000


def test_cli_builds_hidden_autostart_command(tmp_path: Path) -> None:
    args = argparse.Namespace(host="127.0.0.1", backend_port=8123, frontend_port=3123, open=False)
    command = build_autostart_command(tmp_path, args)
    assert "--root" in command
    assert str(tmp_path) in command
    assert "--no-open" in command
    script = build_hidden_vbs(command)
    assert "WScript.Shell" in script
    assert ", 0, False" in script
