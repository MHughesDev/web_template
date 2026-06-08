"""Request-ID correlation middleware.

Generates (or propagates an inbound) ``X-Request-ID`` header, binds it into
structlog's contextvars so every log line emitted while handling the request
carries it automatically, and echoes it back on the response.
Controlled by settings.REQUEST_ID_ENABLED.
"""

from __future__ import annotations

from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: object) -> Response:
        request_id = request.headers.get(_REQUEST_ID_HEADER) or str(uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response: Response = await call_next(request)  # type: ignore[operator]
        finally:
            structlog.contextvars.clear_contextvars()

        response.headers[_REQUEST_ID_HEADER] = request_id
        return response
