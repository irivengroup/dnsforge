from __future__ import annotations

# Centralized system command wrapper; shell is never enabled.
import subprocess  # nosec B404


class CommandExecutor:
    def run(self, command: list[str], dry_run: bool = True) -> list[str]:
        self._validate_command(command)
        if dry_run:
            return command

        result = subprocess.run(command, text=True, check=False)  # nosec B603
        if result.returncode != 0:
            raise RuntimeError(f"command failed: {' '.join(command)}")

        return command

    @staticmethod
    def _validate_command(command: list[str]) -> None:
        if not command:
            raise ValueError("command cannot be empty")
        if any(not part or "\x00" in part for part in command):
            raise ValueError("command contains an invalid argument")
