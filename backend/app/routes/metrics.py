from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import func
from ..db import get_db
from ..models import Agent

router = APIRouter(prefix="/metrics", tags=["metrics"])

_started_at = datetime.now(timezone.utc)

@router.get("/live")
def live():
    return {"live": True}

@router.get("/ready")
def ready():
    return {"ready": True}

@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    uptime_s = (now - _started_at).total_seconds()
    total_agents = db.query(func.count(Agent.id)).scalar() or 0
    published = db.query(func.count(Agent.id)).filter(Agent.published==True).scalar() or 0
    return {"uptime_s": uptime_s, "agents_total": int(total_agents), "agents_published": int(published)}
