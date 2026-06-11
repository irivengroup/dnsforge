from __future__ import annotations

from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory, DnsForgeCli


def build_parser():
    return DnsForgeArgumentParserFactory().build()


def main(argv: list[str] | None = None) -> int:
    return DnsForgeCli().run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
