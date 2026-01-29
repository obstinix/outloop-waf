"""
Secure Endpoint

Protected endpoint demonstrating WAF security capabilities.
Processes requests that pass through WAF inspection.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from api.core.logic import get_service
from api.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SecurePayload(BaseModel):
    """Request payload for secure endpoint."""
    data: str = Field(..., min_length=1, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None


class SecureResponse(BaseModel):
    """Response model for secure endpoint."""
    success: bool
    processed_at: str
    message: str
    waf_verified: bool


@router.get("/secure/info")
async def secure_info(request: Request) -> Dict[str, Any]:
    """
    Get information about the secure endpoint.
    
    Returns:
        Endpoint documentation and WAF status
    """
    waf_request_id = request.headers.get("x-waf-request-id", "unknown")
    
    return {
        "endpoint": "/api/secure",
        "description": "WAF-protected secure endpoint",
        "waf_enabled": True,
        "waf_request_id": waf_request_id,
        "methods": ["GET", "POST"],
        "protection": [
            "SQL Injection",
            "Cross-Site Scripting (XSS)",
            "Path Traversal",
            "Command Injection"
        ]
    }


@router.post("/secure/process", response_model=SecureResponse)
async def process_secure_data(
    payload: SecurePayload,
    request: Request
) -> SecureResponse:
    """
    Process data through the secure WAF-protected endpoint.
    
    If this endpoint is reached, the request has passed
    all WAF security checks.
    
    Args:
        payload: The data to process
        request: The HTTP request object
        
    Returns:
        Processing confirmation with WAF verification status
    """
    service = get_service()
    # If request reaches this endpoint, it passed WAF inspection
    # WAF would have blocked it with 403 if threat detected
    waf_protected = True
    
    logger.info(f"Processing secure request | WAF verified: {waf_protected}")
    
    # Process the data
    result = service.process_request({"data": payload.data})
    
    return SecureResponse(
        success=True,
        processed_at=datetime.utcnow().isoformat(),
        message="Data processed successfully through WAF-protected endpoint",
        waf_verified=waf_protected
    )


@router.get("/secure/test")
async def test_waf_protection(
    request: Request,
    payload: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test endpoint for demonstrating WAF protection.
    
    Try sending malicious payloads to see WAF blocking in action.
    
    Args:
        payload: Optional test payload (will be inspected by WAF)
        
    Returns:
        Confirmation that request passed WAF inspection
    """
    waf_request_id = request.headers.get("x-waf-request-id", "unknown")
    
    return {
        "status": "passed",
        "message": "Request passed WAF inspection",
        "waf_request_id": waf_request_id,
        "received_payload": payload[:50] if payload else None,
        "tip": "Try sending SQL injection or XSS payloads to test WAF blocking"
    }
