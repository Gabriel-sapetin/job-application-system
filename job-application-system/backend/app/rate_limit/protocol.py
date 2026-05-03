from typing import Protocol, Tuple


class RateLimiter(Protocol):
    """Backend-agnostic sliding-window rate limiter (called from ASGI middleware)."""

    async def check(self, client_key: str) -> Tuple[bool, str]:
        """Return (allowed, error_detail). When allowed is True, error_detail is ignored."""

