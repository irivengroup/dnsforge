#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from dnsforge.contracts.event_contracts import PUBLIC_EVENT_CONTRACT

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (ROOT / "src" / "dnsforge" / "api", ROOT / "src" / "dnsforge" / "application")


def main() -> int:
    source = "\n".join(path.read_text(encoding="utf-8") for root in SOURCE_ROOTS for path in root.rglob("*.py"))
    missing = [event.name for event in PUBLIC_EVENT_CONTRACT.required_events if event.name not in source]
    if missing:
        print("DNSForge event coverage failed:")
        for event in missing:
            print(f"- missing event publication or contract reference: {event}")
        return 1
    print(f"Event Coverage: 100% ({len(PUBLIC_EVENT_CONTRACT.required_events)} required events referenced)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
