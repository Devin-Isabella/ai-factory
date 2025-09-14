from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets

router = APIRouter()

class SandboxStart(BaseModel):
    bot_id: int

class SandboxStop(BaseModel):
    session_id: str

@router.post("/sandbox/start")
async def sandbox_start(inp: SandboxStart):
    # ephemeral: just mint a session id, pretend it expires in 15 min
    sid = secrets.token_urlsafe(16)
    return {"session_id": sid, "bot_id": inp.bot_id, "expires_in": 900}

@router.post("/sandbox/stop")
async def sandbox_stop(inp: SandboxStop):
    # nothing to delete (we never persisted)
    return {"status":"stopped","session_id": inp.session_id}
