from __future__ import annotations

import subprocess


class CommandExecutor:
    def run(self, command: list[str], dry_run: bool = True) -> list[str]:
        if dry_run:
            return command

        result = subprocess.run(command, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"command failed: {' '.join(command)}")

        return command
