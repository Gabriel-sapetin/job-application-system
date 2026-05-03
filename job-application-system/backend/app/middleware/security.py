"""
HTTP security headers (HSTS, CSP, referrer policy, etc.).

HTTPS detection honours X-Forwarded-Proto when TRUST_PROXY is enabled (nginx, Cloudflare, tunnels).
"""

import os
import logging
from typing import Optional

from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("jobtrack")

# Swagger / OpenAPI paths use inline scripts — skip CSP here to avoid breaking /docs.
_CSP_SKIP_PATH_PREFIXES = ("/docs", "/redoc", "/openapi.json")


def _trust_proxy() -> bool:
    return os.getenv("TRUST_PROXY", "").lower() in ("1", "true", "yes")


def _env_flag(name: str, default_true: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if raw == "":
        return default_true
    return raw in ("1", "true", "yes", "on")


def request_is_https(request: Request) -> bool:
    """Treat connection as HTTPS if URL scheme is https or proxy says so."""
    if request.url.scheme == "https":
        return True
    if _trust_proxy():
        proto = request.headers.get("x-forwarded-proto", "")
        if proto:
            first = proto.split(",")[0].strip().lower()
            if first == "https":
                return True
        fwd = request.headers.get("forwarded", "")
        for part in fwd.split(","):
            for token in part.split(";"):
                t = token.strip().lower()
                if t.startswith("proto="):
                    val = t.split("=", 1)[1].strip()
                    if val == "https":
                        return True
    return False


def _hsts_value() -> Optional[str]:
    if not _env_flag("HSTS_ENABLE", True):
        return None
    max_age = max(0, int(os.getenv("HSTS_MAX_AGE", "31536000")))
    parts = [f"max-age={max_age}"]
    if _env_flag("HSTS_INCLUDE_SUBDOMAINS", False):
        parts.append("includeSubDomains")
    if _env_flag("HSTS_PRELOAD", False):
        parts.append("preload")
    return "; ".join(parts)


def _default_csp() -> str:
    """Relaxed CSP for SPA-style inline scripts; tighten with CONTENT_SECURITY_POLICY in production."""
    return (
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "img-src 'self' data: https: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self' http: https: ws: wss: data: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "object-src 'none'"
    )


def _csp_header_value() -> str:
    override = os.getenv("CONTENT_SECURITY_POLICY", "").strip()
    if override:
        return override
    return _default_csp()


def _should_emit_csp(path: str) -> bool:
    if not _env_flag("CSP_ENABLE", True):
        return False
    for prefix in _CSP_SKIP_PATH_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return False
    return True


def apply_security_headers(request: Request, response: Response) -> None:
    if not _env_flag("SECURITY_HEADERS_ENABLED", True):
        return

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault(
        "Referrer-Policy", os.getenv("REFERRER_POLICY", "strict-origin-when-cross-origin")
    )

    fp = os.getenv("PERMISSIONS_POLICY", "").strip()
    if fp:
        response.headers.setdefault("Permissions-Policy", fp)

    if _should_emit_csp(request.url.path):
        csp_value = _csp_header_value()
        if _env_flag("CSP_REPORT_ONLY", False):
            response.headers.setdefault("Content-Security-Policy-Report-Only", csp_value)
        else:
            response.headers.setdefault("Content-Security-Policy", csp_value)

    frame_opt = os.getenv("X_FRAME_OPTIONS", "DENY").strip()
    if frame_opt:
        response.headers.setdefault("X-Frame-Options", frame_opt)

    if request_is_https(request):
        hv = _hsts_value()
        if hv:
            response.headers.setdefault("Strict-Transport-Security", hv)


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    try:
        apply_security_headers(request, response)
    except Exception:
        logger.exception("Security headers failed for %s", request.url.path)
    return response
