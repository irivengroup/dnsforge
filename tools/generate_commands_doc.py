#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))

    from dnsforge.application.docs.commands_doc_service import CommandDocumentationService
    from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory

    parser = argparse.ArgumentParser(
        description="Generate docs/COMMANDS.md from the DNSForge CLI parser without invoking the privileged CLI."
    )
    parser.add_argument(
        "--output",
        default="docs/COMMANDS.md",
        help="Documentation output path, relative to the repository root unless absolute.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    CommandDocumentationService().write(DnsForgeArgumentParserFactory().build(), output)
    print(f"Generated {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
