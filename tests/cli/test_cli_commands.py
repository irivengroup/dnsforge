from __future__ import annotations

from pathlib import Path

from dnsforge.interfaces.cli.main import build_parser

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_cli_parser_accepts_active_commands() -> None:
    parser = build_parser()
    commands = [
        ["validate", "proxy", "proxy01", "--type", "forwarder"],
        ["validate", "proxy", "proxy01", "--type", "hybrid"],
        ["validate", "authoritative", "auth01"],
        ["render", "proxy", "proxy01", "--type", "forwarder"],
        ["render", "authoritative", "auth01"],
        ["deploy", "proxy", "proxy01", "--type", "forwarder", "--dry-run"],
        ["deploy", "authoritative", "auth01", "--dry-run"],
        ["initialize", "--render-only"],
        ["initialize", "--dry-run"],
        ["initialize", "--apply"],
        ["zone", "list"],
        ["zone", "get", "--name", "example.com"],
        [
            "zone",
            "create",
            "--name",
            "example.com",
            "--type",
            "master",
            "--views",
            "external,internal",
            "--reason",
            "unit test change",
        ],
        ["zone", "disable", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "enable", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "retire", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "delete", "--name", "example.com", "--reason", "unit test change"],
        ["catalog", "status"],
        ["catalog", "enable", "--reason", "unit test change"],
        ["catalog", "sync", "--reason", "unit test change"],
        ["catalog", "disable", "--reason", "unit test change"],
        ["catalog", "list"],
        ["catalog", "validate"],
    ]
    for command in commands:
        parser.parse_args(command)


def test_dnsforge_console_script_is_declared() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "dnsforge =" in pyproject
    assert "dnsforge.interfaces.cli.main:main" in pyproject
    assert not (PROJECT_ROOT / "bin").exists()
