import importlib

from fastapi.testclient import TestClient


def test_main_module_imports():
    """Ensure main module imports without raising (regression for Cloud Run)."""
    module = importlib.import_module("main")
    assert hasattr(module, "app")


def test_health_endpoint_responds():
    """App should expose /health once routers load."""
    module = importlib.import_module("main")
    with TestClient(module.app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json().get("status") in {"healthy", "degraded"}
