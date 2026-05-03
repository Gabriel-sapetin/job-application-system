import logging
import os
from functools import lru_cache

from starlette.requests import Request

from app.rate_limit.memory import MemoryRateLimiter
from app.rate_limit.protocol import RateLimiter

logger = logging.getLogger("jobtrack")


class _PassthroughLimiter:
    """No-op limiter when rate limiting is disabled or deferred to a gateway."""

    async def check(self, client_key: str) -> tuple[bool, str]:
        return True, ""


def _global_limit_from_env() -> int:
    return max(1, int(os.getenv("RATE_LIMIT_GLOBAL_LIMIT", "100")))


def _global_window_from_env() -> int:
    return max(1, int(os.getenv("RATE_LIMIT_GLOBAL_WINDOW", "60")))


def _trust_proxy() -> bool:
    return os.getenv("TRUST_PROXY", "").lower() in ("1", "true", "yes")


def _redis_fallback_to_memory() -> bool:
    return os.getenv("RATE_LIMIT_REDIS_FALLBACK_TO_MEMORY", "").lower() in ("1", "true", "yes")


@lru_cache
def _build_limiter() -> RateLimiter:
    backend = os.getenv("RATE_LIMIT_BACKEND", "memory").strip().lower()
    limit = _global_limit_from_env()
    window = _global_window_from_env()

    if backend in ("disabled", "off", "none", "trust_gateway"):
        if backend == "trust_gateway":
            logger.info("Rate limiting: PASSTHROUGH (trust_gateway); enforce at CDN/reverse-proxy.")
        else:
            logger.info("Rate limiting: DISABLED.")
        return _PassthroughLimiter()

    if backend == "memory":
        logger.info(f"Rate limiting: MEMORY (limit={limit} per {window}s; not shared across workers).")
        return MemoryRateLimiter(limit=limit, window_seconds=window)

    if backend == "redis":
        redis_url = os.getenv("REDIS_URL", "").strip()
        if not redis_url:
            message = (
                "RATE_LIMIT_BACKEND=redis requires REDIS_URL, but REDIS_URL is empty. "
                "Set REDIS_URL (e.g. redis://localhost:6379/0), or switch RATE_LIMIT_BACKEND=memory."
            )
            if _redis_fallback_to_memory():
                logger.warning("%s Falling back to memory backend.", message)
                return MemoryRateLimiter(limit=limit, window_seconds=window)
            raise RuntimeError(message)

        try:
            from redis.asyncio import from_url as redis_from_url
            from app.rate_limit.redis import RedisRateLimiter
        except Exception as exc:
            raise RuntimeError(
                "RATE_LIMIT_BACKEND=redis requires the 'redis' Python package. "
                "Install dependencies from requirements.txt."
            ) from exc

        redis_client = redis_from_url(redis_url, encoding="utf-8", decode_responses=True)
        logger.info("Rate limiting: REDIS (limit=%s per %ss).", limit, window)
        return RedisRateLimiter(redis_client=redis_client, limit=limit, window_seconds=window)

    logger.warning(f"Unknown RATE_LIMIT_BACKEND={backend!r}; using memory.")
    return MemoryRateLimiter(limit=limit, window_seconds=window)


def get_rate_limiter() -> RateLimiter:
    """Singleton limiter instance for app lifetime."""
    return _build_limiter()


def extract_client_key(request: Request) -> str:
    """Client identity for rate limits (usually IP behind optional reverse proxy)."""
    if _trust_proxy():
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",", 1)[0].strip() or "unknown"
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
