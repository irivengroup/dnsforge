from __future__ import annotations

from dataclasses import dataclass
import subprocess

@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

class CommandRunner:
    def run(self, command: list[str], check: bool = False, timeout: int = 60) -> CommandResult:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
        result = CommandResult(command, completed.returncode, completed.stdout, completed.stderr)
        if check and not result.ok:
            raise RuntimeError(f"command failed: {' '.join(command)}\n{result.stderr}")
        return result
