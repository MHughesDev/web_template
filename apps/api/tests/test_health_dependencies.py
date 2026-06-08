import asyncio
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.routes._health import DependencyStatus, probe_dependencies
from app.core.config import settings


def test_dependencies_endpoint_requires_superuser(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/utils/health/dependencies/")
    assert r.status_code == 401


def test_dependencies_endpoint_returns_aggregated_status(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    ok_status = DependencyStatus(service="database", ok=True, detail="reachable")

    with patch(
        "app.api.routes.utils.probe_dependencies",
        new=AsyncMock(return_value={"database": ok_status}),
    ):
        r = client.get(
            f"{settings.API_V1_STR}/utils/health/dependencies/",
            headers=superuser_token_headers,
        )

    assert r.status_code == 200
    body = r.json()
    assert body["database"]["ok"] is True
    assert body["database"]["service"] == "database"


def test_dependencies_endpoint_returns_404_when_disabled(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    disabled_settings = settings.model_copy(
        update={"HEALTH_DEPENDENCIES_ENABLED": False}
    )
    with patch("app.api.routes.utils.settings", disabled_settings):
        r = client.get(
            f"{settings.API_V1_STR}/utils/health/dependencies/",
            headers=superuser_token_headers,
        )
    assert r.status_code == 404


def test_probe_dependencies_reports_not_configured_services() -> None:
    unconfigured = settings.model_copy(
        update={"SMTP_HOST": None, "SENTRY_DSN": None, "HEALTH_CHECK_URLS": []}
    )

    db_status = DependencyStatus(service="database", ok=True, detail="reachable")
    with patch(
        "app.api.routes._health.probe_database",
        new=AsyncMock(return_value=db_status),
    ):
        results = asyncio.run(probe_dependencies(unconfigured))

    assert results["smtp"].detail == "not configured"
    assert results["sentry"].detail == "not configured"


def test_no_secrets_appear_in_dependency_status_response(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/utils/health/dependencies/",
        headers=superuser_token_headers,
    )
    body_text = r.text
    assert settings.POSTGRES_PASSWORD not in body_text
    assert settings.SECRET_KEY not in body_text
    assert "SMTP_PASSWORD" not in body_text
