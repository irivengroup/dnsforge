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
        ["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"],
        ["zone", "disable", "--name", "example.com"],
        ["zone", "enable", "--name", "example.com"],
        ["zone", "delete", "--name", "example.com"],
    ]
    for command in commands:
        parser.parse_args(command)


def test_bin_dnsforge_entrypoint_exists() -> None:
    assert (PROJECT_ROOT / "bin/dnsforge").is_file()
