from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Agent

router = APIRouter(prefix="/publisher", tags=["publisher"])

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    # MVP stub: counts adoptions by parent
    published = db.query(Agent).filter(Agent.published==True).all()
    items = [{"bot_id": a.id, "name": a.name, "adoptions": db.query(Agent).filter(Agent.parent_id==a.id).count(), "revenue_share_estimate": 0.0, "next_payout_on": None} for a in published]
    return {"published_bots": items, "cycle_length_days": 14}
