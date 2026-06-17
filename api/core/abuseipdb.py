"""
AbuseIPDB Threat Intelligence Client

Provides IP reputation lookups using the AbuseIPDB API v2 check endpoint.
Caches lookup scores to prevent excess latency and save API usage limit.
"""
import os
import time
from typing import Union

import httpx

from api.core.redis_client import redis
from api.utils.logger import get_logger

logger = get_logger(__name__)

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")
ABUSEIPDB_THRESHOLD = int(os.getenv("ABUSEIPDB_THRESHOLD", "85"))
CACHE_TTL = 86400  # 24 hours in seconds


class AbuseIPDBClient:
    """Wrapper client for querying AbuseIPDB endpoint."""

    def __init__(self) -> None:
        # Memory cache fallback: {ip: (score, expire_timestamp)}
        self._memory_cache: dict[str, tuple[int, float]] = {}

    async def get_abuse_score(self, ip: str) -> Union[int, None]:
        """
        Query AbuseIPDB confidence score for the given IP address.
        Attempts to read from Redis cache first, falling back to local memory.
        Returns None if API key is not configured or query failed.
        """
        if not ABUSEIPDB_API_KEY:
            return None

        # Check cached entry
        cached = self._get_cached_score(ip)
        if cached is not None:
            return cached

        # Query endpoint
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                headers = {
                    "Key": ABUSEIPDB_API_KEY,
                    "Accept": "application/json"
                }
                params = {
                    "ipAddress": ip,
                    "maxAgeInDays": "30"
                }
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    headers=headers,
                    params=params
                )
                if response.status_code == 200:
                    data = response.json()
                    score = data.get("data", {}).get("abuseConfidenceScore")
                    if score is not None:
                        self._set_cached_score(ip, score)
                        return int(score)
                else:
                    logger.warning(
                        f"AbuseIPDB query failed with status {response.status_code}: {response.text}"
                    )
        except Exception as e:
            logger.error(f"Error querying AbuseIPDB for IP {ip}: {e}")

        return None

    def _get_cached_score(self, ip: str) -> Union[int, None]:
        """Read score from Redis or memory cache."""
        now = time.time()
        if redis:
            try:
                val = redis.get(f"cache:abuseipdb:{ip}")
                if val is not None:
                    return int(val)
            except Exception as e:
                logger.warning(f"Failed to read AbuseIPDB cache from Redis: {e}")
        else:
            if ip in self._memory_cache:
                score, expires_at = self._memory_cache[ip]
                if now < expires_at:
                    return score
                else:
                    del self._memory_cache[ip]
        return None

    def _set_cached_score(self, ip: str, score: int) -> None:
        """Write score to Redis or memory cache."""
        now = time.time()
        if redis:
            try:
                redis.set(f"cache:abuseipdb:{ip}", str(score))
                redis.expire(f"cache:abuseipdb:{ip}", CACHE_TTL)
            except Exception as e:
                logger.warning(f"Failed to write AbuseIPDB cache to Redis: {e}")
        else:
            self._memory_cache[ip] = (score, now + CACHE_TTL)


abuse_ipdb_client = AbuseIPDBClient()
