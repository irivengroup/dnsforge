#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from _cli_inventory import ROOT, iter_leaf_commands

sys.path.insert(0, str(ROOT / "src"))

from dnsforge.contracts.api_contracts import PUBLIC_API_CONTRACT

REQUIRED_DOMAIN_COMMANDS = {
    "zone": "dnsforge zone",
    "catalog": "dnsforge catalog",
    "cluster": "dnsforge cluster",
    "dnssec": "dnsforge dnssec",
    "migration": "dnsforge migrate",
    "disaster": "dnsforge disaster",
    "readiness": "dnsforge readiness",
}

API_MODULES = {
    "ZoneApi": "dnsforge.interfaces.api.zones",
    "CatalogApi": "dnsforge.interfaces.api.catalog",
    "ClusterApi": "dnsforge.interfaces.api.cluster",
    "DnssecApi": "dnsforge.interfaces.api.dnssec",
    "MigrationApi": "dnsforge.interfaces.api.migration",
    "DisasterRecoveryApi": "dnsforge.interfaces.api.disaster",
    "ReadinessApi": "dnsforge.interfaces.api.readiness",
}


def main() -> int:
    commands = set(iter_leaf_commands())
    errors: list[str] = []
    for domain, command_prefix in REQUIRED_DOMAIN_COMMANDS.items():
        if not any(command == command_prefix or command.startswith(command_prefix + " ") for command in commands):
            errors.append(f"missing CLI command family for API domain {domain!r}: {command_prefix}")

    for capability in PUBLIC_API_CONTRACT.capabilities:
        class_name, method_name = capability.api.split(".", 1)
        module_name = API_MODULES.get(class_name)
        if module_name is None:
            errors.append(f"unknown API class in contract: {class_name}")
            continue
        api_class = getattr(importlib.import_module(module_name), class_name, None)
        if api_class is None or not hasattr(api_class, method_name):
            errors.append(f"missing API method declared in contract: {capability.api}")

    if errors:
        print("DNSForge CLI/API parity failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"CLI/API Parity: PASS ({len(PUBLIC_API_CONTRACT.capabilities)} API capabilities checked)")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(main())
