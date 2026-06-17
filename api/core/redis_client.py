"""
Redis client singleton backed by Upstash REST API.
Falls back to an in-memory stub when UPSTASH_REDIS_REST_URL is not set
(local development / CI environments).
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from upstash_redis import Redis
    _url = os.getenv("UPSTASH_REDIS_REST_URL")
    _token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

    if _url and _token:
        redis = Redis(url=_url, token=_token)
        logger.info("Redis: connected to Upstash")
    else:
        redis = None
        logger.warning("Redis: UPSTASH env vars not set — falling back to in-memory")
except ImportError:
    redis = None
    logger.warning("Redis: upstash-redis not installed — falling back to in-memory")
