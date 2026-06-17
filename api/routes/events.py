"""
Real-time events endpoint.
Exposes a Server-Sent Events (SSE) stream of blocked threat events.
"""
import asyncio
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.waf.engine import WAFEngine
from api.routes.health import get_engine

router = APIRouter(prefix="/api", tags=["events"])

@router.get("/events/threats")
async def threat_event_stream(engine: WAFEngine = Depends(get_engine), test: bool = False):
    """SSE stream of real-time threat block events."""
    async def event_generator():
        q = engine.subscribe()
        try:
            yield "data: {\"type\":\"connected\"}\n\n"
            if test:
                return
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"  # SSE keepalive comment
        finally:
            engine.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


