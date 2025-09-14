from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..db import get_db, get_current_user_optional
from ..models import Agent
from ..schemas import AgentCard

router = APIRouter(prefix="/store", tags=["store"])

def to_card(a: Agent) -> AgentCard:
    return AgentCard(
        id=a.id,
        name=a.name or "",
        description=a.description or "",
        category=a.category or "",
        published=bool(a.published),
        tone_profile=a.tone_profile or "",
        safety_rating=a.safety_rating or "",
        safety_score=float(a.safety_score) if a.safety_score is not None else None,
        lineage_display=a.lineage_display or "",
        last_safety_check=a.last_safety_check.isoformat() if a.last_safety_check else None,
        usage_cost=float(a.usage_cost) if a.usage_cost is not None else None,
    )

def apply_sort(query, sort: str):
    s = (sort or "created_desc").lower()
    if s == "created_asc":
        return query.order_by(Agent.created_at.asc())
    if s == "name_asc":
        return query.order_by(Agent.name.asc())
    if s == "name_desc":
        return query.order_by(Agent.name.desc())
    # default
    return query.order_by(Agent.created_at.desc())

@router.get("/search", operation_id="store_search_cards")
def store_search(
    q: str = Query("", description="optional search"),
    page: int = Query(1, ge=1),
    size: int = Query(5, ge=1, le=50),
    sort: str = Query("created_desc"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
):
    base = db.query(Agent)
    if user and "id" in user:
        base = base.filter(or_(Agent.owner_id==user["id"], Agent.published==True))
    else:
        base = base.filter(Agent.published==True)

    if q:
        like = f"%{q}%"
        base = base.filter(or_(Agent.name.ilike(like), Agent.description.ilike(like)))

    total = base.count()
    base = apply_sort(base, sort)

    rows = base.offset((page-1)*size).limit(size).all()
    items = [to_card(r).dict() for r in rows]

    return {"items": items, "page": page, "size": size, "total": int(total), "sort": sort}
