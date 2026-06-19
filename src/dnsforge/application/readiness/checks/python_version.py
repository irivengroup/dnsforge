from __future__ import annotations

import sys

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus


class PythonVersionCheck:
    name = "Python Version"
    critical = True

    def __init__(self, minimum: tuple[int, int] = (3, 9)) -> None:
        self.minimum = minimum

    def run(self) -> ReadinessResult:
        current = sys.version_info[:2]
        if current < self.minimum:
            return ReadinessResult(
                self.name,
                ReadinessStatus.FAILED,
                f"Python {current[0]}.{current[1]} is below supported minimum {self.minimum[0]}.{self.minimum[1]}",
                critical=self.critical,
            )
        return ReadinessResult(
            self.name,
            ReadinessStatus.PASS,
            f"Python {current[0]}.{current[1]} meets supported minimum {self.minimum[0]}.{self.minimum[1]}",
            critical=self.critical,
        )
