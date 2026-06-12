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
        ["deploy", "proxy", "proxy01", "--type", "forwarder", "--dry-run"],
        ["deploy", "authoritative", "auth01", "--dry-run"],
        ["proxy", "initialize", "proxy01", "--type", "forwarder", "--render-only"],
        ["proxy", "initialize", "proxy01", "--type", "forwarder", "--dry-run"],
        ["authoritative", "initialize", "auth01", "--render-only"],
        ["authoritative", "initialize", "auth01", "--dry-run"],
        ["zone", "list"],
        ["zone", "get", "--name", "example.com"],
        ["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"],
        ["zone", "disable", "--name", "example.com"],
        ["zone", "enable", "--name", "example.com"],
        ["zone", "delete", "--name", "example.com"],
        ["proxy", "initialize", "proxy01"],
    ]
    for command in commands:
        parser.parse_args(command)
    assert ProxyType.choices() == ["forwarder", "hybrid"]


def test_bin_dnsforge_entrypoint_exists() -> None:
    assert (PROJECT_ROOT / "bin/dnsforge").is_file()


def test_proxy_initialize_defaults_to_hybrid() -> None:
    parser = build_parser()
    args = parser.parse_args(["proxy", "initialize"])
    assert args.proxy_type == "hybrid"
    assert args.node == "local"
