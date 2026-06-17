"""
OUTERLOOP WAF - FastAPI Entry Point

Perimeter-Grade Web Attack Protection with middleware-based request inspection.
Configured for Vercel serverless deployment.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from api.routes import admin, events, gravity, health, metrics, secure
from api.utils.logger import get_logger
from api.waf.engine import waf_engine
from api.waf.middleware import WAFMiddleware

logger = get_logger(__name__)

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application components on startup."""
    logger.info("WAF Application starting up...")
    logger.info("Security middleware initialized")
    logger.info(f"Static files directory: {STATIC_DIR}")
    yield
    logger.info("WAF Application shutting down...")


app = FastAPI(
    title="OUTERLOOP WAF",
    description="Perimeter-Grade Web Attack Protection with middleware-based request inspection",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration for frontend integration
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://outerloop-waf.vercel.app,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# WAF Middleware - Core security layer
app.add_middleware(WAFMiddleware, engine=waf_engine)

# Route registration
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(secure.router, prefix="/api", tags=["Secure"])
app.include_router(gravity.router, prefix="/api", tags=["Gravity"])
app.include_router(admin.router)
app.include_router(events.router)
app.include_router(metrics.router)


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend page with cache-busting headers."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(
            index_path,
            media_type="text/html",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse(
        content="<h1>WAF API</h1><p>Frontend not found. Visit <a href='/api/docs'>/api/docs</a> for API documentation.</p>",
        status_code=200
    )


# Vercel automatically detects the FastAPI 'app' variable for serverless functions
