"""Structured logging configuration (structlog).

Configures ``structlog`` to render JSON in non-local environments (and a
human-readable console format locally), and bridges stdlib ``logging`` calls
(used throughout the codebase, e.g. ``logging.getLogger(__name__)``) through
the same processor chain via ``structlog.stdlib.ProcessorFormatter`` — no need
to rewrite existing loggers.

New code should prefer ``get_logger(__name__)`` for structured, context-bound
output (e.g. request IDs bound by ``RequestContextMiddleware`` are
automatically attached to every log line emitted during that request).
"""

from __future__ import annotations

import logging

import structlog

from app.core.config import Settings

get_logger = structlog.get_logger

_SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_logging(settings: Settings) -> None:
    """Configure structlog + bridge stdlib logging through the same pipeline.

    Idempotent — safe to call multiple times (e.g. once at import time, once
    in test fixtures) since it fully replaces the root handler set each time.
    """
    if not settings.STRUCTLOG_ENABLED:
        logging.basicConfig(level=logging.INFO)
        return

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.ENVIRONMENT != "local"
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_SHARED_PROCESSORS,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
