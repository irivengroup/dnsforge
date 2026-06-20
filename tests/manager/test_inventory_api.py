from dnsforge_manager.application.core.manager_application import create_app
from dnsforge_manager.interfaces.api.fastapi_app import create_fastapi_app


def test_manager_inventory_api_core_create_and_list():
    app = create_app()

    assert app.inventory_sites()["sites"] == []
    created = app.create_inventory_site({"site_id": "emea", "name": "EMEA"})
    assert created["site"]["site_id"] == "emea"

    app.create_inventory_cluster({"cluster_id": "c1", "name": "Cluster 1", "site": "emea"})
    app.register_inventory_agent(
        {
            "fingerprint": "fp-api",
            "hostname": "dns01",
            "version": "14.2.0",
            "profile": "authoritative",
            "site": "emea",
            "cluster": "c1",
            "status": "READY",
        }
    )

    assert app.inventory_clusters()["clusters"][0]["cluster_id"] == "c1"
    assert app.inventory_agents()["agents"][0]["fingerprint"] == "fp-api"
    assert app.inventory_environments()["environments"][0]["environment_id"] == "production"
    assert app.inventory_agent_status()["status"] == "READY"


def test_manager_inventory_routes_are_exposed_without_fastapi_dependency():
    api = create_fastapi_app(create_app())
    routes = set()
    for route in getattr(api, "routes", []):
        if hasattr(route, "method"):
            routes.add((route.method, route.path))
        else:
            for method in getattr(route, "methods", set()):
                routes.add((method, getattr(route, "path", "")))

    assert ("GET", "/inventory/sites") in routes
    assert ("POST", "/inventory/sites") in routes
    assert ("GET", "/inventory/clusters") in routes
    assert ("POST", "/inventory/clusters") in routes
    assert ("GET", "/inventory/agents") in routes
    assert ("POST", "/inventory/agents") in routes
    assert ("GET", "/inventory/environments") in routes
