from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class InitializeStep:
    name: str
    command: list[str] | None = None
    description: str = ""


@dataclass
class InitializePlan:
    role: str
    node: str
    render_root: Path | None = None
    dry_run: bool = False
    backup_before_apply: bool = True
    backend: str = "python-bind-deployer"
    steps: list[InitializeStep] = field(default_factory=list)

    def add_step(self, name: str, command: list[str] | None = None, description: str = "") -> None:
        self.steps.append(InitializeStep(name=name, command=command, description=description))

    def summary(self) -> str:
        lines = [
            "Initialize plan",
            f"role={self.role}",
            f"node={self.node}",
            f"backend={self.backend}",
            f"mode={'dry-run' if self.dry_run else 'apply'}",
            f"backup_before_apply={'yes' if self.backup_before_apply else 'no'}",
        ]
        if self.render_root is not None:
            lines.append(f"render_root={self.render_root}")

        lines.append("")

        for idx, step in enumerate(self.steps, 1):
            command = " ".join(step.command or [])
            if command:
                lines.append(f"{idx}. {step.name} :: {command}")
            else:
                lines.append(f"{idx}. {step.name} :: {step.description}")

        return "\n".join(lines)
