"""
Prometheus Metrics Route.
Exposes WAF performance and blocking statistics.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    Counter, Gauge, Histogram,
    generate_latest, CONTENT_TYPE_LATEST
)
from api.routes.health import get_engine

router = APIRouter(tags=["metrics"])

# Metrics registry
requests_total = Counter(
    "waf_requests_total",
    "Total requests analyzed by WAF",
    ["method", "status"]
)
blocked_total = Counter(
    "waf_blocked_total",
    "Total requests blocked by WAF",
    ["rule"]
)
rule_hits = Counter(
    "waf_rule_hits_total",
    "Times each WAF rule fired",
    ["rule_name"]
)
response_time = Histogram(
    "waf_response_time_seconds",
    "WAF middleware processing time",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1.0]
)
blocked_ips_gauge = Gauge(
    "waf_blocked_ips_current",
    "Number of IPs currently in the blocklist"
)

@router.get("/api/metrics")
async def metrics_endpoint(engine=Depends(get_engine)):
    # Update gauge from current engine state
    stats = engine.get_stats()
    blocked_ips_gauge.set(stats.get("blocked_ips", 0))
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
