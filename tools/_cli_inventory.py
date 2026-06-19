from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


def build_parser() -> argparse.ArgumentParser:
    from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory

    return DnsForgeArgumentParserFactory().build()


def _find_subparser_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def iter_leaf_commands(parser: argparse.ArgumentParser | None = None) -> tuple[str, ...]:
    root = parser or build_parser()
    return tuple(sorted(_walk(root)))


def _walk(parser: argparse.ArgumentParser) -> Iterable[str]:
    nested = _find_subparser_action(parser)
    if nested is None:
        yield parser.prog
        return
    if parser.prog != "dnsforge" and not getattr(nested, "required", False):
        yield parser.prog
    for name in sorted(nested.choices):
        yield from _walk(nested.choices[name])
