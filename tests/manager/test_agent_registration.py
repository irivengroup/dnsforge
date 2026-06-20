from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService


def test_agent_registration_requires_operational_metadata():
    service = CentralInventoryService()
    agent = service.register_agent(
        {
            "fingerprint": "fp-001",
            "hostname": "dns-proxy-01",
            "version": "14.2.0",
            "profile": "proxy-hybrid",
            "site": "bonapriso",
            "cluster": "edge-proxy",
            "status": "WARNING",
        }
    )

    assert agent.fingerprint == "fp-001"
    assert agent.hostname == "dns-proxy-01"
    assert agent.version == "14.2.0"
    assert agent.profile == "proxy-hybrid"
    assert agent.site == "bonapriso"
    assert agent.cluster == "edge-proxy"
    assert service.aggregate_readiness()["status"] == "WARNING"
