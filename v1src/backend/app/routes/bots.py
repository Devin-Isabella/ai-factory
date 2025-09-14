from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/bots", tags=["bots"])

# Fake in-memory store for now
FAKE_BOTS: List[Dict] = []


@router.get("/")
def list_bots():
    """Return all bots (placeholder)."""
    return {"bots": FAKE_BOTS}


@router.post("/")
def create_bot(bot: Dict):
    """Create a new bot (name, description, tone)."""
    FAKE_BOTS.append(bot)
    return {"msg": "Bot created", "bot": bot}
