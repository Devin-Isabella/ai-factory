from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Agent, AuditLog

router = APIRouter(prefix="/owner", tags=["publish"])

class PublishBody(BaseModel):
    bot_id: int
    publish: bool

@router.post("/publish")
def publish_toggle(body: PublishBody, db: Session = Depends(get_db)):
    ag = db.query(Agent).filter(Agent.id==body.bot_id).first()
    if not ag:
        raise HTTPException(status_code=404, detail="bot not found")
    ag.published = bool(body.publish)
    db.add(AuditLog(event_type=("publish" if ag.published else "unpublish"), bot_id=ag.id, payload={"published": ag.published}))
    db.commit()
    return {"bot_id": ag.id, "published": ag.published}
