from __future__ import annotations

import shutil

from dnsforge.shared.errors import DnsForgeError


class BindPrerequisites:
    REQUIRED_COMMANDS: tuple[str, ...] = ("named-checkconf", "rndc", "systemctl")

    def assert_available(self) -> None:
        missing = [command for command in self.REQUIRED_COMMANDS if shutil.which(command) is None]
        if missing:
            raise DnsForgeError(
                "BIND is not ready on this node. Missing command(s): "
                + ", ".join(missing)
                + ". Run the DNSForge installer from install/ before dnsforge initialize."
            )
