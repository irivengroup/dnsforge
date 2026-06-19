#!/usr/bin/env python3
from __future__ import annotations

import importlib

from dnsforge.contracts.api_contracts import PUBLIC_API_CONTRACT


REQUIRED_APIS = {
    "ZoneApi": "dnsforge.interfaces.api.zones",
    "CatalogApi": "dnsforge.interfaces.api.catalog",
    "ClusterApi": "dnsforge.interfaces.api.cluster",
    "DnssecApi": "dnsforge.interfaces.api.dnssec",
    "MigrationApi": "dnsforge.interfaces.api.migration",
    "DisasterRecoveryApi": "dnsforge.interfaces.api.disaster",
    "ReadinessApi": "dnsforge.interfaces.api.readiness",
}


def main() -> int:
    errors: list[str] = []
    for class_name, module_name in REQUIRED_APIS.items():
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):
            errors.append(f"missing API facade: {module_name}.{class_name}")
    for capability in PUBLIC_API_CONTRACT.capabilities:
        class_name, method_name = capability.api.split(".", 1)
        module_name = REQUIRED_APIS.get(class_name)
        if module_name is None:
            errors.append(f"contract references unknown API class: {class_name}")
            continue
        api_class = getattr(importlib.import_module(module_name), class_name, None)
        if api_class is None or not hasattr(api_class, method_name):
            errors.append(f"contract references missing method: {capability.api}")
    if errors:
        print("DNSForge API coverage failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"API Coverage: 100% ({len(PUBLIC_API_CONTRACT.capabilities)} capabilities covered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
