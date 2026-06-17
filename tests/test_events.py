"""
Threat events SSE tests.
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_events_stream_connect(async_client: AsyncClient):
    async with async_client.stream("GET", "/api/events/threats?test=true") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Read the first line (connection confirmation)
        lines = response.aiter_lines()
        first_line = await lines.__anext__()
        assert first_line == 'data: {"type":"connected"}'





