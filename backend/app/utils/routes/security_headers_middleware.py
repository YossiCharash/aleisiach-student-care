from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, hsts_max_age_seconds: int | None = None) -> None:
        super().__init__(app)
        self._hsts_max_age_seconds = hsts_max_age_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if self._hsts_max_age_seconds is not None:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self._hsts_max_age_seconds}; includeSubDomains"
            )
        return response
