from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db, get_current_user
from ..models import Agent

router = APIRouter(prefix="/admin", tags=["admin"])

def _ensure_admin(user):
    # Simple local rule: user id 1 is admin
    if not user or "id" not in user or user["id"] != 1:
        raise HTTPException(status_code=403, detail="admin only")

@router.get("/summary")
def summary(db: Session = Depends(get_db), user = Depends(get_current_user)):
    _ensure_admin(user)
    total_agents = db.query(func.count(Agent.id)).scalar() or 0
    published    = db.query(func.count(Agent.id)).filter(Agent.published==True).scalar() or 0
    owners       = db.query(func.count(func.distinct(Agent.owner_id))).scalar() or 0
    return {"agents_total": int(total_agents), "agents_published": int(published), "owners": int(owners)}

@router.get("/bots")
def bots(db: Session = Depends(get_db), user = Depends(get_current_user)):
    _ensure_admin(user)
    rows = db.query(Agent.id, Agent.name, Agent.published).order_by(Agent.id.desc()).limit(50).all()
    return {"items": [{"id": r[0], "name": r[1], "published": bool(r[2])} for r in rows]}
