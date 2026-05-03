import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, DefaultDict, Tuple


class MemoryRateLimiter:
    """Per-process sliding window. Does not synchronize across workers (use Redis for that)."""

    def __init__(self, limit: int, window_seconds: int):
        self._limit = limit
        self._window = float(window_seconds)
        self._log: DefaultDict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, client_key: str) -> Tuple[bool, str]:
        async with self._lock:
            now = time.time()
            hits = self._log[client_key]
            cutoff = now - self._window
            while hits and hits[0] < cutoff:
                hits.popleft()
            if len(hits) >= self._limit:
                return (
                    False,
                    f"Too many requests. Limit is {self._limit} per {int(self._window)}s.",
                )
            hits.append(now)
            return True, ""
