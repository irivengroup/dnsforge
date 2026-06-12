from __future__ import annotations

from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
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
        ["initialize", "proxy", "proxy01", "--type", "forwarder", "--render-only"],
        ["initialize", "proxy", "proxy01", "--type", "forwarder", "--dry-run"],
        ["initialize", "authoritative", "auth01", "--render-only"],
        ["initialize", "authoritative", "auth01", "--dry-run"],
        ["zone", "list"],
        ["zone", "get", "--name", "example.com"],
        ["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"],
        ["zone", "disable", "--name", "example.com"],
        ["zone", "enable", "--name", "example.com"],
        ["zone", "delete", "--name", "example.com"],
        ["initialize", "proxy", "proxy01"],
    ]
    for command in commands:
        parser.parse_args(command)
    assert ProxyType.choices() == ["forwarder", "hybrid"]


def test_bin_dnsforge_entrypoint_exists() -> None:
    assert (PROJECT_ROOT / "bin/dnsforge").is_file()
