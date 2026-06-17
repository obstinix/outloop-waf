"""
WAF Middleware

FastAPI middleware that intercepts and analyzes all incoming requests
for potential security threats before they reach application handlers.
"""

from collections.abc import Callable
from typing import cast

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from api.utils.logger import get_logger
from api.waf.engine import RequestContext, ThreatLevel, WAFEngine
from api.waf.rate_limiter import rate_limiter

logger = get_logger(__name__)


TRUSTED_PROXIES = {
    # Vercel's proxy ranges — update from Vercel docs if these change
    "76.76.21.0/24",
    "76.223.126.0/24",
}


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
        "/favicon.ico",
        "/api/events/threats",
        "/api/metrics"
    }

    def __init__(self, app, engine: WAFEngine):
        """Initialize the WAF middleware with a shared engine instance."""
        super().__init__(app)
        self.engine = engine
        logger.info("WAF Middleware initialized")

    async def __call__(self, scope, receive, send) -> None:
        """Bypass BaseHTTPMiddleware entirely for long-lived streams and metrics to avoid Starlette bugs."""
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path in ("/api/events/threats", "/api/metrics"):
                await self.app(scope, receive, send)
                return
        await super().__call__(scope, receive, send)



    async def _extract_body(self, request: Request) -> str:
        """Safely extract request body content."""
        try:
            body = await request.body()
            if body:
                return body.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.debug(f"Could not read request body: {e}")
        return ""

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        client_host = request.client.host if request.client else "unknown"

        # Only trust X-Forwarded-For if the connecting IP is a known proxy
        if forwarded and self._is_trusted_proxy(client_host):
            # Take the LAST IP added by our trusted proxy, not the first
            ips = [ip.strip() for ip in forwarded.split(",")]
            return ips[-1]

        if real_ip:
            return real_ip

        return client_host

    def _is_trusted_proxy(self, ip: str) -> bool:
        import ipaddress
        try:
            addr = ipaddress.ip_address(ip)
            for prefix in TRUSTED_PROXIES:
                if addr in ipaddress.ip_network(prefix, strict=False):
                    return True
        except ValueError:
            pass
        return False

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
        import time

        from api.routes.metrics import blocked_total, requests_total, response_time, rule_hits

        start_time = time.perf_counter()

        self.engine.increment_request_counter()
        path = request.url.path

        # Allow bypass paths
        if self._should_bypass(path):
            response = await call_next(request)
            requests_total.labels(method=request.method, status=str(response.status_code)).inc()
            response_time.observe(time.perf_counter() - start_time)
            return cast(Response, response)

        client_ip = self._get_client_ip(request)

        # Rate limit check (before WAF analysis — cheapest gate first)
        # Bypassed for admin endpoints so administrators aren't locked out
        is_limited, limit_name = False, ""
        if not path.startswith("/api/admin"):
            is_limited, limit_name = rate_limiter.is_rate_limited(client_ip)
        if is_limited:
            requests_total.labels(method=request.method, status="429").inc()
            response_time.observe(time.perf_counter() - start_time)
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "limit": limit_name},
                headers={
                    "X-WAF-Rate-Limited": "true",
                    "Retry-After": "60",
                }
            )

        # Build request context for analysis
        headers = dict(request.headers)
        body = await self._extract_body(request)

        context = RequestContext(
            method=request.method,
            path=path,
            query_string=str(request.url.query) if request.url.query else "",
            headers={k.lower(): v for k, v in headers.items()},
            body=body,
            client_ip=client_ip
        )

        # Run WAF analysis
        assessment = self.engine.analyze(context)

        # Block if threat detected
        if assessment.is_threat:
            rule_name = assessment.violations[0]["rule_name"] if assessment.violations else "Blocked IP"

            # Log the block (structured in prod, standard string in dev)
            import os
            if os.getenv("ENVIRONMENT") == "production":
                logger.warning("request_blocked", extra={
                    "extra": {
                        "ip": context.client_ip,
                        "path": path,
                        "method": request.method,
                        "rule": rule_name,
                        "payload_snippet": str(request.url)[:100],
                    }
                })
            else:
                logger.warning(
                    f"Request blocked | ID: {assessment.request_id} | "
                    f"IP: {context.client_ip} | Path: {path} | "
                    f"Level: {assessment.threat_level.value if assessment.threat_level else 'unknown'} | "
                    f"Rule: {rule_name}"
                )

            # Determine blocking behavior based on threat level
            if assessment.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                self.engine.increment_blocked_counter()
                self.engine.emit_threat_event({
                    "ip": context.client_ip,
                    "rule": rule_name,
                    "path": path
                })

                # Prometheus metrics
                requests_total.labels(method=request.method, status="403").inc()
                blocked_total.labels(rule=rule_name).inc()
                for violation in assessment.violations:
                    rule_hits.labels(rule_name=violation["rule_name"]).inc()
                response_time.observe(time.perf_counter() - start_time)

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

        # Prometheus metrics
        requests_total.labels(method=request.method, status=str(response.status_code)).inc()
        if assessment.is_threat:
            for violation in assessment.violations:
                rule_hits.labels(rule_name=violation["rule_name"]).inc()
        response_time.observe(time.perf_counter() - start_time)

        return cast(Response, response)
