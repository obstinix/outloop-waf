"""
Health Check Endpoint

Provides health and readiness checks for the WAF application.
Used by load balancers, orchestrators, and monitoring systems.
"""

from fastapi import APIRouter, Response, Depends
from typing import Dict, Any
from datetime import datetime

from api.core.logic import get_service
from api.waf.engine import WAFEngine, waf_engine
from api.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
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


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(engine: WAFEngine = Depends(get_engine)) -> Dict[str, Any]:
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
async def readiness_check(response: Response) -> Dict[str, Any]:
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
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes-style liveness check.
    
    Simple check that returns 200 if the process is alive.
    """
    return {"status": "alive"}
