from __future__ import annotations

from dataclasses import dataclass

# Centralized subprocess wrapper; shell is never enabled.
import subprocess  # nosec B404


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
        self._validate_command(command)
        completed = subprocess.run(  # nosec B603
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        result = CommandResult(command, completed.returncode, completed.stdout, completed.stderr)
        if check and not result.ok:
            raise RuntimeError(f"command failed: {' '.join(command)}\n{result.stderr}")
        return result

    @staticmethod
    def _validate_command(command: list[str]) -> None:
        if not command:
            raise ValueError("command cannot be empty")
        if any(not part or "\x00" in part for part in command):
            raise ValueError("command contains an invalid argument")
