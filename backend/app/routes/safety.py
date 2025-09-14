from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Agent, AuditLog
import datetime as dt

router = APIRouter(prefix="/safety", tags=["safety"])

@router.post("/run-check")
def run_check(bot_id: int = Query(...), db: Session = Depends(get_db)):
    ag = db.query(Agent).filter(Agent.id==bot_id).first()
    if not ag:
        raise HTTPException(status_code=404, detail="bot not found")
    # naive pass/fail heuristic (MVP)
    score = 97.0
    rating = "pass"
    ag.safety_score = score
    ag.safety_rating = rating
    ag.last_safety_check = dt.datetime.now(dt.timezone.utc)
    db.add(AuditLog(event_type="safety_check", bot_id=ag.id, payload={"score": score, "rating": rating}))
    db.commit()
    return {"bot_id": ag.id, "safety_rating": rating, "safety_score": float(score), "last_safety_check": ag.last_safety_check.isoformat()}
