from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/review/queue")
def review_queue():
    """Temporary placeholder admin review queue."""
    return {"items": []}


@router.post("/review/{bot_id}/approve")
def approve_bot(bot_id: str, payload: dict = None):
    """Approve a bot (mock implementation)."""
    return {"bot_id": bot_id, "status": "approved"}
