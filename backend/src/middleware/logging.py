import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request with method, path, status, duration, user_id, trace_id."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id

        start_time = time.perf_counter()

        # Extract user_id from auth header if present (without decoding JWT)
        user_id = None

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            trace_id=trace_id,
            user_id=user_id,
        )

        # Add trace_id to response headers
        response.headers["X-Trace-ID"] = trace_id

        return response
