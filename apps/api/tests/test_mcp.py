from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.mcp import mount_mcp


def test_mcp_is_not_mounted_when_disabled(client: TestClient) -> None:
    assert settings.MCP_ENABLED is False
    assert not any(getattr(route, "path", "") == "/mcp" for route in app.routes)

    r = client.get("/mcp")
    assert r.status_code == 404


def test_mount_mcp_registers_mcp_route_and_requires_auth() -> None:
    test_app = FastAPI(title="mcp-test-app")

    @test_app.get("/ping", operation_id="ping", tags=["health"])
    def ping() -> bool:
        """Trivial ping endpoint for MCP scaffold testing."""
        return True

    mount_mcp(test_app)

    assert any(
        str(getattr(route, "path", "")).startswith("/mcp") for route in test_app.routes
    )

    with TestClient(test_app) as test_client:
        r = test_client.get("/mcp")
        assert r.status_code in (401, 406)
