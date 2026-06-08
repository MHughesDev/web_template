"""Dependency-readiness probes.

Aggregates read-only connectivity checks for whatever external dependencies
this deployment actually has configured: the database (always), SMTP (if
``SMTP_HOST`` is set), Sentry (if ``SENTRY_DSN`` is set), and an arbitrary
list of HTTP health-check URLs (``HEALTH_CHECK_URLS``).

All probes are strictly read-only and never log or return secret values
(SMTP credentials, the Sentry DSN's embedded key): only host/port/reachability
information is surfaced. Controlled by settings.HEALTH_DEPENDENCIES_ENABLED.
"""

from __future__ import annotations

import smtplib
import time
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DependencyStatus(BaseModel):
    service: str
    ok: bool
    detail: str
    latency_ms: float | None = None


def _elapsed_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 2)


async def probe_database(settings: Settings) -> DependencyStatus:
    """Check that the database is reachable with a trivial ``SELECT 1``."""
    from sqlmodel import Session, select

    from app.core.db import engine

    start = time.monotonic()
    try:
        with Session(engine) as session:
            session.exec(select(1))
        return DependencyStatus(
            service="database",
            ok=True,
            detail=f"reachable at {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}",
            latency_ms=_elapsed_ms(start),
        )
    except Exception as exc:
        logger.warning("health_probe_failed", service="database", error=str(exc))
        return DependencyStatus(
            service="database",
            ok=False,
            detail=f"unreachable at {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}",
            latency_ms=_elapsed_ms(start),
        )


async def probe_smtp(settings: Settings) -> DependencyStatus:
    """Open a connection and issue EHLO/NOOP only — never authenticate."""
    if not settings.SMTP_HOST:
        return DependencyStatus(service="smtp", ok=True, detail="not configured")

    start = time.monotonic()
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    try:
        with smtplib.SMTP(
            host=host, port=port, timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS
        ) as client:
            if settings.SMTP_TLS:
                client.starttls()
            client.ehlo()
            client.noop()
        return DependencyStatus(
            service="smtp",
            ok=True,
            detail=f"reachable at {host}:{port}",
            latency_ms=_elapsed_ms(start),
        )
    except Exception as exc:
        logger.warning("health_probe_failed", service="smtp", error=str(exc))
        return DependencyStatus(
            service="smtp",
            ok=False,
            detail=f"unreachable at {host}:{port}",
            latency_ms=_elapsed_ms(start),
        )


async def probe_sentry(settings: Settings) -> DependencyStatus:
    """Plain HTTP reachability check of the Sentry host — never capture_message."""
    if not settings.SENTRY_DSN:
        return DependencyStatus(service="sentry", ok=True, detail="not configured")

    start = time.monotonic()
    host = urlparse(str(settings.SENTRY_DSN)).hostname or "unknown"
    try:
        async with httpx.AsyncClient(
            timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS
        ) as client:
            await client.get(f"https://{host}")
        return DependencyStatus(
            service="sentry",
            ok=True,
            detail=f"reachable at {host}",
            latency_ms=_elapsed_ms(start),
        )
    except Exception as exc:
        logger.warning("health_probe_failed", service="sentry", error=str(exc))
        return DependencyStatus(
            service="sentry",
            ok=False,
            detail=f"unreachable at {host}",
            latency_ms=_elapsed_ms(start),
        )


async def probe_http_url(name: str, url: str, settings: Settings) -> DependencyStatus:
    """Plain GET reachability check for an arbitrary configured HTTP URL."""
    start = time.monotonic()
    host = urlparse(url).hostname or url
    try:
        async with httpx.AsyncClient(
            timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS
        ) as client:
            response = await client.get(url)
        return DependencyStatus(
            service=name,
            ok=response.is_success,
            detail=f"{response.status_code} from {host}",
            latency_ms=_elapsed_ms(start),
        )
    except Exception as exc:
        logger.warning("health_probe_failed", service=name, error=str(exc))
        return DependencyStatus(
            service=name,
            ok=False,
            detail=f"unreachable at {host}",
            latency_ms=_elapsed_ms(start),
        )


async def probe_dependencies(settings: Settings) -> dict[str, DependencyStatus]:
    """Run all configured probes and return a mapping of service name to status."""
    results: dict[str, DependencyStatus] = {}

    for status in (
        await probe_database(settings),
        await probe_smtp(settings),
        await probe_sentry(settings),
    ):
        results[status.service] = status

    for index, url in enumerate(settings.HEALTH_CHECK_URLS):
        name = f"http_{index}_{urlparse(str(url)).hostname or index}"
        results[name] = await probe_http_url(name, str(url), settings)

    return results
