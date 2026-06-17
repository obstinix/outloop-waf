"""
Redis client singleton backed by Upstash REST API.
Falls back to an in-memory stub when UPSTASH_REDIS_REST_URL is not set
(local development / CI environments).
"""
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

redis: Any = None

try:
    from upstash_redis import Redis
    _url = os.getenv("UPSTASH_REDIS_REST_URL")
    _token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

    if _url and _token:
        redis = Redis(url=_url, token=_token)
        logger.info("Redis: connected to Upstash")
    else:
        logger.warning("Redis: UPSTASH env vars not set — falling back to in-memory")
except ImportError:
    logger.warning("Redis: upstash-redis not installed — falling back to in-memory")
