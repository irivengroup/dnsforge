from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class WorkerSizing:
    """Deterministic worker sizing derived from local server characteristics."""

    cpu_count: int
    memory_bytes: int | None = None
    min_workers: int = 1
    max_workers: int = 32

    @classmethod
    def detect(cls, *, max_workers: int = 32) -> "WorkerSizing":
        return cls(cpu_count=os.cpu_count() or 1, memory_bytes=_detect_memory_bytes(), max_workers=max_workers)

    def for_items(self, item_count: int, *, io_bound: bool = True) -> int:
        if item_count <= 0:
            return 0
        cpu = max(1, self.cpu_count)
        calculated = cpu * 4 if io_bound else cpu
        if self.memory_bytes is not None:
            # Keep a conservative 64 MiB budget per worker for large fleet operations.
            memory_bound = max(1, self.memory_bytes // (64 * 1024 * 1024))
            calculated = min(calculated, int(memory_bound))
        return max(self.min_workers, min(item_count, calculated, self.max_workers))


class ParallelExecutor:
    """Small, bounded concurrency adapter for Manager fan-out operations."""

    def __init__(self, sizing: WorkerSizing | None = None) -> None:
        self.sizing = sizing or WorkerSizing.detect()

    def map_ordered(self, items: Sequence[T], function: Callable[[T], R], *, io_bound: bool = True) -> tuple[R, ...]:
        workers = self.sizing.for_items(len(items), io_bound=io_bound)
        if workers <= 1:
            return tuple(function(item) for item in items)
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dnsforge-manager") as pool:
            return tuple(pool.map(function, items))

    async def amap_ordered(
        self,
        items: Sequence[T],
        function: Callable[[T], R],
        *,
        io_bound: bool = True,
    ) -> tuple[R, ...]:
        workers = self.sizing.for_items(len(items), io_bound=io_bound)
        if workers <= 1:
            return tuple(function(item) for item in items)
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dnsforge-manager-async") as pool:
            tasks = [loop.run_in_executor(pool, function, item) for item in items]
            results = await asyncio.gather(*tasks)
        return tuple(results)


def _detect_memory_bytes() -> int | None:
    meminfo = "/proc/meminfo"
    try:
        with open(meminfo, encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return int(parts[1]) * 1024
    except OSError:
        return None
    return None
