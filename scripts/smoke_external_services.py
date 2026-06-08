"""Read-only, secret-safe connectivity smoke test for configured external services.

Probes whatever this deployment actually has configured — database, SMTP,
Sentry — using the same read-only primitives as the dependency-health
aggregator endpoint (app.api.routes._health), and reports OK / FAILED / not
configured for each. Fails fast (no retry loop) and never prints secret
values (SMTP_PASSWORD, SMTP_USER, the Sentry DSN's embedded key).

Exit code 0 if every *configured* service is reachable, non-zero otherwise.
"""

from __future__ import annotations

import asyncio
import sys

from app.api.routes._health import (
    DependencyStatus,
    probe_database,
    probe_sentry,
    probe_smtp,
)
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging(settings)
logger = get_logger("smoke_external_services")


def _report(status: DependencyStatus) -> bool:
    if status.detail == "not configured":
        logger.info(
            "smoke_probe", service=status.service, result="skipped (not configured)"
        )
    elif status.ok:
        logger.info(
            "smoke_probe",
            service=status.service,
            result="OK",
            detail=status.detail,
            latency_ms=status.latency_ms,
        )
    else:
        logger.error(
            "smoke_probe",
            service=status.service,
            result="FAILED",
            detail=status.detail,
        )
    return status.ok


async def _run() -> int:
    statuses = [
        await probe_database(settings),
        await probe_smtp(settings),
        await probe_sentry(settings),
    ]
    all_ok = True
    for status in statuses:
        if not _report(status):
            all_ok = False
    return 0 if all_ok else 1


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
