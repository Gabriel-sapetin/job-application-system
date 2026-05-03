import time
from typing import Tuple

from redis.asyncio import Redis


class RedisRateLimiter:
    """Redis-backed fixed-window limiter shared across workers/instances."""

    def __init__(self, redis_client: Redis, limit: int, window_seconds: int, prefix: str = "rl"):
        self._redis = redis_client
        self._limit = limit
        self._window = max(1, int(window_seconds))
        self._prefix = prefix

    async def check(self, client_key: str) -> Tuple[bool, str]:
        now = int(time.time())
        window_start = now - (now % self._window)
        redis_key = f"{self._prefix}:{client_key}:{window_start}"

        pipe = self._redis.pipeline()
        pipe.incr(redis_key, 1)
        pipe.expire(redis_key, self._window + 1)
        results = await pipe.execute()
        current = int(results[0] or 0)

        if current > self._limit:
            detail = f"Too many requests. Limit is {self._limit} per {self._window}s."
            return False, detail
        return True, ""
