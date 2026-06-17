"""
Sliding window rate limiter using Redis sorted sets.
Falls back to in-memory LRU when Redis is unavailable.
"""
import time
import os
from collections import defaultdict
from typing import Tuple
from api.core.redis_client import redis as _redis

RATE_LIMITS = {
    "burst":   (int(os.getenv("RATE_BURST_REQUESTS", "20")),  int(os.getenv("RATE_BURST_SECONDS", "1"))),
    "global":  (int(os.getenv("RATE_GLOBAL_REQUESTS", "300")), int(os.getenv("RATE_GLOBAL_SECONDS", "60"))),
}

class RateLimiter:
    def __init__(self):
        # In-memory fallback: {ip: [(timestamp, count), ...]}
        self._windows: dict = defaultdict(list)

    def is_rate_limited(self, ip: str) -> Tuple[bool, str]:
        """Returns (is_limited, limit_name)."""
        now = time.time()

        for limit_name, (max_requests, window_seconds) in RATE_LIMITS.items():
            if _redis:
                limited = self._check_redis(ip, limit_name, max_requests, window_seconds, now)
            else:
                limited = self._check_memory(ip, limit_name, max_requests, window_seconds, now)

            if limited:
                return True, limit_name

        return False, ""

    def _check_redis(self, ip: str, limit_name: str, max_req: int, window: int, now: float) -> bool:
        key = f"ratelimit:{limit_name}:{ip}"
        pipeline = _redis.pipeline()
        pipeline.zremrangebyscore(key, 0, now - window)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(now): now})
        pipeline.expire(key, window * 2)
        results = pipeline.execute()
        current_count = results[1]
        return current_count >= max_req

    def _check_memory(self, ip: str, limit_name: str, max_req: int, window: int, now: float) -> bool:
        key = f"{limit_name}:{ip}"
        # Remove old entries
        self._windows[key] = [t for t in self._windows[key] if now - t < window]
        count = len(self._windows[key])
        self._windows[key].append(now)
        return count >= max_req

rate_limiter = RateLimiter()
