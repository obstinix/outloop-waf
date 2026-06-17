"""
Admin API — protected by WAF_ADMIN_KEY header.
All endpoints require X-Admin-Key: <WAF_ADMIN_KEY> in request headers.
"""
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from api.routes.health import get_engine
from api.waf.engine import WAFEngine

router = APIRouter(prefix="/api/admin", tags=["admin"])

def require_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")):
    expected = os.getenv("WAF_ADMIN_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API not configured")
    if x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return x_admin_key

class BlockIPRequest(BaseModel):
    ip: str
    reason: str = ""

# --- IP Blocklist ---

@router.post("/blocklist", dependencies=[Depends(require_admin_key)])
async def block_ip(body: BlockIPRequest, engine: WAFEngine = Depends(get_engine)):
    success = engine.block_ip(body.ip)
    if not success:
        raise HTTPException(status_code=422, detail="Invalid IP address")
    return {"blocked": body.ip, "reason": body.reason}

@router.delete("/blocklist/{ip}", dependencies=[Depends(require_admin_key)])
async def unblock_ip(ip: str, engine: WAFEngine = Depends(get_engine)):
    success = engine.unblock_ip(ip)
    return {"unblocked": ip, "was_present": success}

@router.get("/blocklist", dependencies=[Depends(require_admin_key)])
async def get_blocklist(engine: WAFEngine = Depends(get_engine)):
    if engine._use_redis():
        from api.core.redis_client import redis as _redis
        from api.waf.engine import BLOCKED_IPS_KEY
        # Decode bytes from redis sets to string
        members = _redis.smembers(BLOCKED_IPS_KEY) or []
        ips = [ip.decode("utf-8") if isinstance(ip, bytes) else ip for ip in members]
    else:
        ips = list(engine._local_blocked_ips)
    return {"blocked_ips": ips, "count": len(ips)}

# --- Stats ---

@router.get("/stats", dependencies=[Depends(require_admin_key)])
async def get_stats(engine: WAFEngine = Depends(get_engine)):
    return engine.get_stats()

# --- Rules ---

@router.get("/rules", dependencies=[Depends(require_admin_key)])
async def list_rules(engine: WAFEngine = Depends(get_engine)):
    return {
        "rules": [
            {
                "id": rule.id,
                "name": rule.name,
                "pattern": rule.pattern.pattern,
                "threat_level": rule.threat_level.value,
                "description": rule.description
            }
            for rule in engine.rules.get_all_rules()
        ],
        "count": len(engine.rules.get_all_rules()),
    }
