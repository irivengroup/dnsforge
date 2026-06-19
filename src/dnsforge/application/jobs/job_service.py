from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from dnsforge.domain.events.model import utc_now
from dnsforge.domain.jobs.model import JobDefinition, JobRun
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class JobRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"jobs": [], "runs": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def list_jobs(self) -> list[JobDefinition]:
        data = self._read()
        return [JobDefinition(**dict(item)) for item in data.get("jobs", [])]

    def save_job(self, job: JobDefinition) -> None:
        data = self._read()
        jobs = [dict(item) for item in data.get("jobs", [])]
        jobs = [item for item in jobs if item.get("job_id") != job.job_id]
        jobs.append(
            {
                "job_id": job.job_id,
                "name": job.name,
                "command": job.command,
                "description": job.description,
                "enabled": job.enabled,
                "metadata": job.metadata,
            }
        )
        data["jobs"] = sorted(jobs, key=lambda item: str(item.get("job_id", "")))
        self._write(data)

    def get_job(self, job_id: str) -> JobDefinition:
        for job in self.list_jobs():
            if job.job_id == job_id:
                return job
        raise ValueError(f"unknown job: {job_id}")

    def append_run(self, run: JobRun) -> None:
        data = self._read()
        runs = [dict(item) for item in data.get("runs", [])]
        runs.append(
            {
                "run_id": run.run_id,
                "job_id": run.job_id,
                "status": run.status,
                "started_at": run.started_at,
                "finished_at": run.finished_at,
                "exit_code": run.exit_code,
                "output": run.output,
            }
        )
        data["runs"] = runs
        self._write(data)

    def list_runs(self) -> list[JobRun]:
        data = self._read()
        return [JobRun(**dict(item)) for item in data.get("runs", [])]


class JobService:
    """Local job foundation for recurring DNSForge operations."""

    def __init__(self, paths: ProjectPaths) -> None:
        self.repository = JobRepository(paths.settings_root / "jobs.json")

    def bootstrap_defaults(self) -> None:
        defaults = [
            JobDefinition(
                "cluster-audit",
                "Cluster audit",
                ["dnsforge", "cluster", "audit"],
                "Audit authoritative cluster consistency.",
            ),
            JobDefinition(
                "catalog-sync",
                "Catalog sync",
                ["dnsforge", "catalog", "sync", "--reason", "scheduled-catalog-sync"],
                "Synchronize catalog zone publications.",
            ),
            JobDefinition(
                "dnssec-expiry-check",
                "DNSSEC expiry check",
                ["dnsforge", "dnssec", "check-expiry"],
                "Check DNSSEC key expiry windows.",
            ),
        ]
        existing = {job.job_id for job in self.repository.list_jobs()}
        for job in defaults:
            if job.job_id not in existing:
                self.repository.save_job(job)

    def list(self) -> str:
        self.bootstrap_defaults()
        rows = ["JOB ID\tSTATUS\tNAME\tCOMMAND"]
        for job in self.repository.list_jobs():
            rows.append(
                f"{job.job_id}\t{'enabled' if job.enabled else 'disabled'}\t{job.name}\t{' '.join(job.command)}"
            )
        return "\n".join(rows)

    def show(self, job_id: str) -> str:
        self.bootstrap_defaults()
        job = self.repository.get_job(job_id)
        return json.dumps(
            {
                "job_id": job.job_id,
                "name": job.name,
                "command": job.command,
                "description": job.description,
                "enabled": job.enabled,
                "metadata": job.metadata,
            },
            indent=2,
            sort_keys=True,
        )

    def run(self, job_id: str, *, dry_run: bool = False) -> str:
        self.bootstrap_defaults()
        job = self.repository.get_job(job_id)
        if not job.enabled:
            raise ValueError(f"job disabled: {job_id}")
        output = "dry-run: " + " ".join(job.command) if dry_run else "queued: " + " ".join(job.command)
        self.repository.append_run(
            JobRun(
                run_id=uuid4().hex,
                job_id=job.job_id,
                status="dry-run" if dry_run else "queued",
                finished_at=utc_now(),
                exit_code=0,
                output=output,
            )
        )
        return output

    def cancel(self, job_id: str) -> str:
        self.bootstrap_defaults()
        self.repository.get_job(job_id)
        self.repository.append_run(
            JobRun(run_id=uuid4().hex, job_id=job_id, status="cancelled", finished_at=utc_now(), exit_code=0)
        )
        return f"cancelled: {job_id}"

    def history(self) -> str:
        rows = ["RUN ID\tJOB ID\tSTATUS\tEXIT\tSTARTED"]
        for run in self.repository.list_runs():
            rows.append(
                f"{run.run_id}\t{run.job_id}\t{run.status}\t{run.exit_code if run.exit_code is not None else '-'}\t{run.started_at}"
            )
        return "\n".join(rows)
