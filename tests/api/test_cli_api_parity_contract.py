from __future__ import annotations

import ast
from pathlib import Path

from dnsforge.api import DnsForgeApplicationApi, MigrationApi
from dnsforge.api.parity import CLI_API_PARITY_PRINCIPLES, LOCAL_CLI_COMMANDS
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory


def _top_level_commands() -> set[str]:
    parser = DnsForgeArgumentParserFactory().build()
    for action in parser._actions:  # argparse has no public accessor for subparser choices.
        choices = getattr(action, "choices", None)
        if choices:
            return set(choices)
    raise AssertionError("top-level DNSForge subcommands not found")


def test_local_cli_domains_remain_available() -> None:
    assert set(LOCAL_CLI_COMMANDS).issubset(_top_level_commands())


def test_cli_does_not_depend_on_api_facades_for_local_dispatch() -> None:
    source = Path("src/dnsforge/interfaces/cli/application.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_modules.update(
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
    )

    assert not any(module == "dnsforge.api" or module.startswith("dnsforge.api.") for module in imported_modules)


def test_application_api_exposes_migration_facade(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))
    api = DnsForgeApplicationApi(ProjectPaths(tmp_path))

    assert isinstance(api.migration, MigrationApi)


def test_cli_api_parity_principles_are_declared() -> None:
    assert "DNSForge CLI is a primary local administration interface." in CLI_API_PARITY_PRINCIPLES
    assert "No operational feature may become API-only or GUI-only." in CLI_API_PARITY_PRINCIPLES
