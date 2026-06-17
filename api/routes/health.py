"""
Health Check Endpoint

Provides health and readiness checks for the WAF application.
Used by load balancers, orchestrators, and monitoring systems.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Response

from api.core.logic import get_service
from api.utils.logger import get_logger
from api.waf.engine import WAFEngine, waf_engine

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Health status and basic system information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "waf-api",
        "version": "1.0.0"
    }


def get_engine() -> WAFEngine:
    """Dependency provider for the WAFEngine singleton."""
    return waf_engine


@router.get("/health/detailed", response_model=dict[str, Any])
async def detailed_health_check(engine: WAFEngine = Depends(get_engine)) -> dict[str, Any]:
    """
    Detailed health check with component status.

    Returns:
        Comprehensive health information including all components
    """
    service = get_service()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "waf-api",
        "version": "1.0.0",
        "uptime_seconds": round(service.uptime_seconds, 2),
        "components": {
            "waf_engine": {
                "status": "operational",
                "stats": engine.get_stats()
            },
            "database": {
                "status": "not_required",
                "message": "Stateless architecture"
            }
        }
    }


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, Any]:
    """
    Kubernetes-style readiness check.

    Returns 200 if service is ready to accept traffic,
    503 if service is not ready.
    """
    # In a stateless WAF, we're always ready if we're running
    is_ready = True

    if not is_ready:
        response.status_code = 503
        return {
            "ready": False,
            "reason": "Service initializing"
        }

    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Kubernetes-style liveness check.

    Simple check that returns 200 if the process is alive.
    """
    return {"status": "alive"}
