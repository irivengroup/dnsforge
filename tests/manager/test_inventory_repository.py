from dnsforge_manager.domain.inventory.models import AgentReadiness
from dnsforge_manager.infrastructure.inventory.central_repository import JsonCentralInventoryRepository
from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService


def test_json_central_inventory_repository_persists_all_aggregates(tmp_path):
    repo = JsonCentralInventoryRepository(tmp_path / "inventory.json")
    service = CentralInventoryService(repo)

    service.create_site({"site_id": "paris", "name": "Paris DC"})
    service.create_cluster({"cluster_id": "auth-a", "name": "Authoritative A", "site": "paris"})
    service.register_agent(
        {
            "fingerprint": "sha256:abc",
            "hostname": "dns01.example.net",
            "version": "14.2.0",
            "profile": "authoritative",
            "site": "paris",
            "cluster": "auth-a",
            "status": "READY",
        }
    )

    reloaded = CentralInventoryService(JsonCentralInventoryRepository(tmp_path / "inventory.json"))
    assert reloaded.list_sites()[0].site_id == "paris"
    assert reloaded.list_clusters()[0].cluster_id == "auth-a"
    assert reloaded.list_agents()[0].fingerprint == "sha256:abc"
    assert reloaded.list_agent_status()[0].readiness is AgentReadiness.READY


def test_inventory_aggregates_worst_agent_readiness():
    service = CentralInventoryService()
    service.update_agent_status({"fingerprint": "a", "readiness": "READY"})
    service.update_agent_status({"fingerprint": "b", "readiness": "FAILED"})

    aggregate = service.aggregate_readiness()

    assert aggregate["status"] == "FAILED"
    assert aggregate["summary"]["READY"] == 1
    assert aggregate["summary"]["FAILED"] == 1
