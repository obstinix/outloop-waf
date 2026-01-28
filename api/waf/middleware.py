"""
WAF Middleware

FastAPI middleware that intercepts and analyzes all incoming requests
for potential security threats before they reach application handlers.
"""

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from api.waf.engine import WAFEngine, RequestContext, ThreatLevel
from api.utils.logger import get_logger

logger = get_logger(__name__)


class WAFMiddleware(BaseHTTPMiddleware):
    """
    Web Application Firewall Middleware
    
    Inspects all incoming HTTP requests for malicious patterns
    and blocks threats before they reach application endpoints.
    """
    
    # Paths that bypass WAF inspection
    BYPASS_PATHS = {
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/health",
        "/favicon.ico"
    }
    
    def __init__(self, app):
        """Initialize the WAF middleware."""
        super().__init__(app)
        self.engine = WAFEngine()
        logger.info("WAF Middleware initialized")
    
    async def _extract_body(self, request: Request) -> str:
        """Safely extract request body content."""
        try:
            body = await request.body()
            if body:
                return body.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.debug(f"Could not read request body: {e}")
        return ""
    
    def _extract_client_ip(self, request: Request) -> str:
        """Extract client IP, respecting proxy headers."""
        # Check X-Forwarded-For first (for proxied requests)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Get first IP in chain
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _should_bypass(self, path: str) -> bool:
        """Check if request path should bypass WAF inspection."""
        return path in self.BYPASS_PATHS or path.startswith("/api/docs")
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process incoming request through WAF analysis.
        
        Args:
            request: The incoming HTTP request
            call_next: The next handler in the chain
            
        Returns:
            Response from application or block response if threat detected
        """
        path = request.url.path
        
        # Allow bypass paths
        if self._should_bypass(path):
            return await call_next(request)
        
        # Build request context for analysis
        headers = dict(request.headers)
        body = await self._extract_body(request)
        
        context = RequestContext(
            method=request.method,
            path=path,
            query_string=str(request.url.query) if request.url.query else "",
            headers={k.lower(): v for k, v in headers.items()},
            body=body,
            client_ip=self._extract_client_ip(request)
        )
        
        # Run WAF analysis
        assessment = self.engine.analyze(context)
        
        # Block if threat detected
        if assessment.is_threat:
            # Log the block
            logger.warning(
                f"Request blocked | ID: {assessment.request_id} | "
                f"IP: {context.client_ip} | Path: {path} | "
                f"Level: {assessment.threat_level.value if assessment.threat_level else 'unknown'}"
            )
            
            # Determine blocking behavior based on threat level
            if assessment.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Forbidden",
                        "message": "Request blocked by Web Application Firewall",
                        "request_id": assessment.request_id
                    },
                    headers={
                        "X-WAF-Block": "true",
                        "X-WAF-Request-ID": assessment.request_id
                    }
                )
            else:
                # Medium/Low threats - log but allow (can be configured)
                logger.info(
                    f"Low-severity threat allowed through | ID: {assessment.request_id}"
                )
        
        # Add WAF headers to response
        response = await call_next(request)
        response.headers["X-WAF-Protected"] = "true"
        response.headers["X-WAF-Request-ID"] = assessment.request_id
        
        return response
