from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db, get_current_user
from ..models import Agent
from ..schemas import AgentCard

router = APIRouter(prefix="/owner", tags=["owner"])

@router.get("/my-bots", operation_id="owner_my_bots_cards")
def my_bots(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    base = db.query(Agent).filter(Agent.owner_id==user["id"])
    total = base.count()
    rows = base.order_by(Agent.id.desc()).offset((page-1)*size).limit(size).all()
    items = []
    for r in rows:
        items.append(AgentCard(
            id=r.id,
            name=r.name or "",
            description=r.description or "",
            category=r.category or "",
            published=bool(r.published),
            tone_profile=r.tone_profile or "",
            safety_rating=r.safety_rating or "",
            safety_score=float(r.safety_score) if r.safety_score is not None else None,
            lineage_display=r.lineage_display or "",
            last_safety_check=r.last_safety_check.isoformat() if r.last_safety_check else None,
            usage_cost=float(r.usage_cost) if r.usage_cost is not None else None,
        ).dict())
    return {"items": items, "page": page, "size": size, "total": int(total)}
