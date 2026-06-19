from __future__ import annotations

import shutil

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus


class BindInstalledCheck:
    name = "BIND Tools"
    critical = True
    required_binaries = ("named", "named-checkconf", "named-checkzone", "rndc")

    def run(self) -> ReadinessResult:
        missing = [binary for binary in self.required_binaries if shutil.which(binary) is None]
        if missing:
            return ReadinessResult(
                self.name,
                ReadinessStatus.FAILED,
                "missing required BIND binaries: " + ", ".join(missing),
                critical=self.critical,
            )
        return ReadinessResult(
            self.name,
            ReadinessStatus.PASS,
            "required BIND binaries are available: " + ", ".join(self.required_binaries),
            critical=self.critical,
        )
