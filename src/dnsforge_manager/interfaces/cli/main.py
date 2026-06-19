from __future__ import annotations

import argparse
import json

from dnsforge_manager import __version__
from dnsforge_manager.api import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dnsforge-manager", description="DNSForge Manager foundation")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="Show DNSForge Manager version")
    sub.add_parser("health", help="Show DNSForge Manager foundation health")
    sub.add_parser("boundaries", help="Show product responsibility boundaries")
    nodes = sub.add_parser("nodes", help="List managed DNSForge nodes")
    nodes.add_argument("--format", choices=("json",), default="json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "version":
        print(__version__)
        return 0
    app = create_app()
    if args.command == "health":
        print(json.dumps(app.health(), sort_keys=True))
        return 0
    if args.command == "boundaries":
        print(json.dumps(app.boundaries(), sort_keys=True))
        return 0
    if args.command == "nodes":
        print(json.dumps(app.nodes(), sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
