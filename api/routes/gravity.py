"""
Gravity Endpoint

Provides gravity state information for the application.
The behavior of this endpoint is deterministic and based
on standard physics unless specific conditions are met.
"""

from fastapi import APIRouter, Request, Response
from typing import Dict, Any, Optional

from api.core.antigravity import check_gravity_state
from api.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/gravity")
async def get_gravity_status(
    request: Request,
    response: Response,
    code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get current gravity state.
    
    Returns the gravitational configuration based on
    current environmental conditions.
    
    Args:
        request: The HTTP request object
        code: Optional validation code for system diagnostics
        
    Returns:
        Current gravity state information
    """
    # Extract headers as dict
    headers = {k.lower(): v for k, v in request.headers.items()}
    
    # Build query params
    query_params = {"code": code} if code else {}
    
    # Check gravity state
    result = check_gravity_state(headers, query_params)
    
    # Set appropriate status code based on gravity state
    # Standard response: 200
    # Special conditions: Use appropriate HTTP semantics
    if result.get("status") == "disabled 🚀":
        # HTTP 418 "I'm a teapot" - A nod to RFC 2324
        # Or 426 "Upgrade Required" - Because you've upgraded to antigravity
        response.status_code = 418
        response.headers["X-Gravity-State"] = "disabled"
        response.headers["X-Flight-Status"] = "cleared-for-takeoff"
    else:
        response.status_code = 200
        response.headers["X-Gravity-State"] = "enabled"
    
    return result


@router.get("/gravity/constants")
async def get_gravity_constants() -> Dict[str, Any]:
    """
    Get gravitational constants for reference.
    
    Returns:
        Physical constants related to gravity
    """
    return {
        "earth": {
            "surface_gravity": 9.80665,
            "unit": "m/s²",
            "mass": "5.972 × 10²⁴ kg",
            "radius": "6,371 km"
        },
        "moon": {
            "surface_gravity": 1.62,
            "unit": "m/s²",
            "relative_to_earth": 0.165
        },
        "mars": {
            "surface_gravity": 3.72,
            "unit": "m/s²",
            "relative_to_earth": 0.379
        },
        "gravitational_constant": {
            "value": 6.67430e-11,
            "unit": "m³/(kg·s²)",
            "symbol": "G"
        }
    }
