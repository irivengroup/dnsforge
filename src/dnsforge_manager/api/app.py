from __future__ import annotations

from dataclasses import asdict
from typing import Any

from dnsforge_manager import __version__
from dnsforge_manager.core.boundaries import PRODUCT_BOUNDARIES
from dnsforge_manager.inventory.service import NodeRegistrationService


class ManagerApplication:
    """Dependency-light Manager application core used by future HTTP adapters."""

    def __init__(self, registration_service: NodeRegistrationService | None = None) -> None:
        self.registration_service = registration_service or NodeRegistrationService()

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "dnsforge-manager", "version": __version__}

    def boundaries(self) -> dict[str, Any]:
        return {"products": [asdict(boundary) for boundary in PRODUCT_BOUNDARIES]}

    def nodes(self) -> dict[str, Any]:
        return {"nodes": [asdict(node) for node in self.registration_service.list_nodes()]}


def create_app() -> ManagerApplication:
    """Return the framework-neutral Manager app core.

    FastAPI integration is intentionally deferred to keep v12.0.0 as a safe foundation that does not add runtime
    dependencies or change the DNSForge local agent behavior.
    """
    return ManagerApplication()
