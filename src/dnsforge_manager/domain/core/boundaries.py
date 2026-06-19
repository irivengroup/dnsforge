from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductBoundary:
    name: str
    responsibility: str
    requires_bind: bool
    may_modify_bind_files: bool


DNSFORGE_BOUNDARY = ProductBoundary(
    name="DNSForge",
    responsibility="Local BIND deployment and configuration agent installed on every managed DNS server.",
    requires_bind=True,
    may_modify_bind_files=True,
)

DNSFORGE_MANAGER_BOUNDARY = ProductBoundary(
    name="DNSForge Manager",
    responsibility="Central management plane for one or more DNSForge agents; it never edits BIND directly.",
    requires_bind=False,
    may_modify_bind_files=False,
)

DNSBEAT_BOUNDARY = ProductBoundary(
    name="DNSBeat",
    responsibility="DNSForge Manager monitoring sub-module for health, metrics and alert readiness.",
    requires_bind=False,
    may_modify_bind_files=False,
)

DNSSYNC_BOUNDARY = ProductBoundary(
    name="DNSSync",
    responsibility="DNSForge Manager synchronization sub-module that orchestrates changes through DNSForge agents.",
    requires_bind=False,
    may_modify_bind_files=False,
)

PRODUCT_BOUNDARIES = (
    DNSFORGE_BOUNDARY,
    DNSFORGE_MANAGER_BOUNDARY,
    DNSBEAT_BOUNDARY,
    DNSSYNC_BOUNDARY,
)
