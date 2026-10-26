"""HTTP security utilities: security headers, session cookie and CSRF protection."""

import os
import re
import uuid
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import api_key_manager


SESSION_COOKIE_NAME = "cev_sid"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year
CSRF_HEADER_NAME = "X-Requested-With"
CSRF_HEADER_VALUE = "cev-rag"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

# UUID4 (current format) or the legacy browser-generated format: session_<timestamp>_<random>
_SESSION_ID_PATTERN = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|session_\d{10,16}_[a-z0-9]{1,16})$"
)

# Paths served with a relaxed CSP so the interactive API docs keep working
_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def is_development() -> bool:
    """Whether the API runs in development mode (relaxes a few checks)."""
    return os.getenv("ENV", "production").strip().lower() == "development"


def is_valid_session_id(value: Optional[str]) -> bool:
    return bool(value) and bool(_SESSION_ID_PATTERN.match(value))


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds defensive HTTP headers to every API response (defense in depth behind nginx)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = response.headers
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if not request.url.path.startswith(_DOCS_PATHS):
            headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
            headers.setdefault("Cache-Control", "no-store")
        if _env_flag("COOKIE_SECURE", True):
            headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        return response


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        path="/api",
        secure=_env_flag("COOKIE_SECURE", True),
        httponly=True,
        samesite="strict",
    )


def get_frontend_session(request: Request, response: Response) -> str:
    """
    Dependency returning the browser session ID stored in the HttpOnly cookie.

    A new session is issued when the cookie is missing or malformed, so every
    frontend request is always bound to exactly one session.
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not is_valid_session_id(session_id):
        session_id = str(uuid.uuid4())
        set_session_cookie(response, session_id)
    return session_id


def csrf_protect(request: Request) -> None:
    """
    Dependency rejecting cross-site state-changing requests.

    Requires the custom X-Requested-With header (which cannot be sent cross-origin
    without a CORS preflight) and an allowed Origin/Referer.
    """
    if request.method in SAFE_METHODS:
        return
    if request.headers.get(CSRF_HEADER_NAME) != CSRF_HEADER_VALUE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing CSRF header.")
    if not api_key_manager.validate_origin(request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid request origin.")
