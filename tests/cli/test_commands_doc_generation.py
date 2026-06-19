from __future__ import annotations

from pathlib import Path

from dnsforge.application.docs.commands_doc_service import CommandDocumentationService
from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory, DnsForgeCommandDispatcher


def test_commands_doc_is_generated_from_real_parser(tmp_path: Path) -> None:
    parser = DnsForgeArgumentParserFactory().build()
    output = tmp_path / "COMMANDS.md"

    written = CommandDocumentationService().write(parser, output)
    content = written.read_text(encoding="utf-8")

    assert written == output
    assert "# DNSForge Commands" in content
    assert "Generated from the DNSForge CLI parser" in content
    assert "`dnsforge migrate" in content
    assert "--to TARGET" in content
    assert "proxy-forwarder" in content
    assert "proxy-hybrid" in content
    assert "`dnsforge generate commands-doc`" in content


def test_generate_commands_doc_dispatch_writes_requested_file(tmp_path: Path) -> None:
    parser = DnsForgeArgumentParserFactory().build()
    args = parser.parse_args(
        [
            "--project-root",
            str(tmp_path),
            "generate",
            "commands-doc",
            "--output",
            "docs/COMMANDS.md",
        ]
    )

    assert DnsForgeCommandDispatcher().dispatch(args) == 0
    generated = tmp_path / "docs" / "COMMANDS.md"
    assert generated.exists()
    assert "`dnsforge zone create`" in generated.read_text(encoding="utf-8")
