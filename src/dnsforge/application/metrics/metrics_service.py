from __future__ import annotations

from dataclasses import dataclass

from dnsforge.application.catalog.catalog_service import CatalogService
from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


@dataclass(frozen=True)
class Metric:
    name: str
    value: int | float
    labels: dict[str, str] | None = None


class MetricsRegistry:
    def __init__(self) -> None:
        self._metrics: list[Metric] = []

    def set(self, name: str, value: int | float, labels: dict[str, str] | None = None) -> None:
        self._metrics = [item for item in self._metrics if item.name != name or item.labels != labels]
        self._metrics.append(Metric(name, value, labels))

    def list(self) -> list[Metric]:
        return list(self._metrics)


class MetricsCollector:
    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def collect(self) -> MetricsRegistry:
        registry = MetricsRegistry()
        catalog_file = self.paths.catalog_file
        registry.set("zones_catalog_file_present", 1 if catalog_file.exists() else 0)
        try:
            catalog_rows = CatalogService(self.paths).list_published().splitlines()
            registry.set("catalog_members", max(0, len(catalog_rows) - 1))
        except Exception:
            registry.set("catalog_members", 0)
        try:
            peers = ClusterService().peers(self.paths.setup_file).splitlines()
            registry.set("cluster_peers", max(0, len(peers) - 1))
        except Exception:
            registry.set("cluster_peers", 0)
        return registry

    def render_text(self) -> str:
        rows = []
        for metric in self.collect().list():
            rows.append(f"{metric.name} {metric.value}")
        return "\n".join(rows)
