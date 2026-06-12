from __future__ import annotations

import os
import sys

from dnsforge.shared.errors import DnsForgeError


class PrivilegeError(DnsForgeError):
    pass


class RootPrivilegeGuard:
    """Enforce privileged execution for every DNSForge command.

    DNSForge owns BIND configuration, service control, permissions and SELinux
    state. Running commands as an unprivileged user would create partial or
    misleading state, so command execution is denied before dispatch.
    """

    def is_root(self) -> bool:
        geteuid = getattr(os, "geteuid", None)
        if geteuid is None:
            return False
        return geteuid() == 0

    def require_root(self) -> None:
        if self.is_root():
            return
        executable = PathLike.executable_name()
        raise PrivilegeError(f"DNSForge commands require elevated privileges. Re-run with: sudo {executable} <command>")


class PathLike:
    @staticmethod
    def executable_name() -> str:
        name = sys.argv[0] or "dnsforge"
        if name.endswith("__main__.py") or name == "-m":
            return "python -m dnsforge.interfaces.cli.main"
        if "dnsforge" in name:
            return "dnsforge"
        return name
