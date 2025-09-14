from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Agent, AuditLog

router = APIRouter(prefix="/adopt", tags=["adoption"])

@router.post("/{bot_id}")
def adopt(bot_id: int, db: Session = Depends(get_db)):
    parent = db.query(Agent).filter(Agent.id==bot_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="bot not found")
    child = Agent(
        name=f"Adopted-{parent.name}",
        description=parent.description,
        category=parent.category,
        tone_profile=parent.tone_profile or "",
        lineage_display=(parent.lineage_display or "") + "→child",
        parent_id=parent.id,
        published=False,  # children not republishable in policy; keep unpublished by default
    )
    db.add(child)
    db.flush()
    db.add(AuditLog(event_type="adopt", bot_id=parent.id, payload={"child_id": child.id}))
    db.commit()
    return {"parent_id": parent.id, "child_id": child.id}
