from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import datetime as dt
from . import db

router = APIRouter()

class BuildRequest(BaseModel):
    name: str
    description: str = "No description"
    keywords: list[str] = []
    visibility: str = "draft"   # "draft" | "active"

def _now():
    return dt.datetime.utcnow().isoformat() + "Z"

@router.post("/builder/scaffold")
def scaffold(req: BuildRequest):
    # ID from normalized name + timestamp
    safe = "".join(c.lower() for c in req.name if c.isalnum() or c in "-_").strip("-_") or "app"
    new_id = f"{safe}-{int(dt.datetime.utcnow().timestamp())}"
    bot = {
        "id": new_id,
        "name": req.name,
        "description": req.description,
        "status": "draft" if req.visibility != "active" else "active",
        "created_at": _now(),
        "updated_at": _now(),
        "keywords": req.keywords,
    }
    db.upsert_bot(bot)  # relies on your existing db helpers
    return bot

@router.post("/builder/publish/{bot_id}")
def publish(bot_id: str):
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(404, "bot not found")
    bot["status"] = "active"
    bot["updated_at"] = _now()
    db.upsert_bot(bot)
    return bot

@router.post("/builder/unpublish/{bot_id}")
def unpublish(bot_id: str):
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(404, "bot not found")
    bot["status"] = "draft"
    bot["updated_at"] = _now()
    db.upsert_bot(bot)
    return bot

@router.get("/builder/check/{bot_id}")
def check(bot_id: str):
    # super-basic “checks”; extend as needed
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(404, "bot not found")
    ok = True
    problems = []
    if len(bot["name"].strip()) < 3:
        ok = False; problems.append("name too short")
    if len(bot["description"].strip()) < 3:
        ok = False; problems.append("description too short")
    return {"ok": ok, "problems": problems, "bot": bot}
