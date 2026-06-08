import logging

import structlog
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.logging import configure_logging, get_logger


def test_configure_logging_uses_json_renderer_in_non_local_env() -> None:
    staging_settings = settings.model_copy(update={"ENVIRONMENT": "staging"})
    try:
        configure_logging(staging_settings)
        formatter = logging.getLogger().handlers[0].formatter
        assert isinstance(formatter, structlog.stdlib.ProcessorFormatter)
        assert any(
            isinstance(p, structlog.processors.JSONRenderer)
            for p in formatter.processors
        )
    finally:
        configure_logging(settings)


def test_get_logger_returns_a_bound_logger() -> None:
    configure_logging(settings)
    logger = get_logger("test")
    assert hasattr(logger, "info")


def test_request_id_header_is_set_and_propagated(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert r.status_code == 200
    assert "X-Request-ID" in r.headers
    assert r.headers["X-Request-ID"]


def test_request_id_is_echoed_when_supplied(client: TestClient) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/utils/health-check/",
        headers={"X-Request-ID": "test-request-id-123"},
    )
    assert r.status_code == 200
    assert r.headers["X-Request-ID"] == "test-request-id-123"


def test_distinct_requests_get_distinct_request_ids(client: TestClient) -> None:
    r1 = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    r2 = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]
