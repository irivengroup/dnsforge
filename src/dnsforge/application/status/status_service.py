from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

from dnsforge.application.network.interface_diagnostics_service import InterfaceDiagnosticsService
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class StatusService:
    def __init__(
        self,
        loader: EnvSettingsLoader | None = None,
        initialize_state: InitializeStateStore | None = None,
    ) -> None:
        self.loader = loader or EnvSettingsLoader()
        self.initialize_state = initialize_state or InitializeStateStore()

    def show(self, setup_file: Path) -> str:
        settings = self.loader.load(setup_file) if setup_file.exists() else {}
        role = settings.get("ROLE", "unknown").strip("'\"")
        proxy_type = settings.get("PROXY_TYPE", "").strip("'\"")
        security = settings.get("SECURITY_PROFILE", "enterprise").strip("'\"")
        profile = "authoritative" if role == "dns-authoritative" else f"proxy-{proxy_type or 'unknown'}"
        lines = [
            f"Hostname: {socket.gethostname()}",
            f"Role: {role}",
            f"Profile: {profile}",
            f"Security Profile: {security}",
            f"RPZ: {settings.get('ENABLE_RPZ', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"DNSSEC: {settings.get('ENABLE_DNSSEC', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"RRL: {settings.get('ENABLE_RRL', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"Setup File: {setup_file}",
        ]

        init_state = self.initialize_state.get_state(setup_file)
        lines.extend(
            [
                "",
                "Initialization:",
                f"  Status: {'initialized' if init_state else 'not initialized'}",
            ]
        )
        if init_state:
            initialized_at = init_state.get("INITIALIZED_AT")
            initialized_role = init_state.get("INITIALIZED_ROLE")
            initialized_node = init_state.get("INITIALIZED_NODE")
            if initialized_at:
                lines.append(f"  Initialized At: {initialized_at}")
            if initialized_role:
                lines.append(f"  Role: {initialized_role}")
            if initialized_node:
                lines.append(f"  Node: {initialized_node}")

        lines.extend(["", *self._network_status_lines(setup_file)])
        return "\n".join(lines)

    def _network_status_lines(self, setup_file: Path) -> list[str]:
        lines = ["Network Interfaces:"]
        if not setup_file.exists():
            lines.append("  Status: unavailable")
            lines.append("  Reason: setup file not found")
            return lines
        try:
            payload = InterfaceDiagnosticsService(setup_file).as_dict()
            interfaces = payload.get("interfaces")
            bind = payload.get("bind")
            if not isinstance(interfaces, dict) or not isinstance(bind, dict):
                raise TypeError("invalid network diagnostic payload")
            for role in ("extranet", "intranet", "admin"):
                item = interfaces.get(role)
                if isinstance(item, dict):
                    nic = self._as_text(item.get("nic"))
                    ip = self._as_text(item.get("ip"))
                    lines.append(f"  {role.capitalize()}: {nic} -> {ip}")
            lines.append(f"  DNS Listen On: {self._as_text(bind.get('DNS_LISTEN_ON'))}")
            lines.append(f"  Admin Listen On: {self._as_text(bind.get('BIND_ADMIN_LISTEN_ON'))}")
            lines.append("  Status: resolved")
        except Exception as exc:  # pragma: no cover - defensive operational status path
            lines.append("  Status: warning")
            lines.append(f"  Reason: {exc}")
        return lines

    def _as_text(self, value: Any) -> str:
        return str(value) if value is not None else ""
