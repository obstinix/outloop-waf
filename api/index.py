"""
Web Application Firewall - FastAPI Entry Point

This module serves as the main entry point for the WAF application,
configured for Vercel serverless deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.waf.middleware import WAFMiddleware
from api.routes import health, secure, gravity
from api.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Web Application Firewall",
    description="Production-grade WAF with middleware-based request inspection",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WAF Middleware - Core security layer
app.add_middleware(WAFMiddleware)

# Route registration
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(secure.router, prefix="/api", tags=["Secure"])
app.include_router(gravity.router, prefix="/api", tags=["Gravity"])


@app.on_event("startup")
async def startup_event():
    """Initialize application components on startup."""
    logger.info("WAF Application starting up...")
    logger.info("Security middleware initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("WAF Application shutting down...")


# Vercel serverless handler
handler = app
