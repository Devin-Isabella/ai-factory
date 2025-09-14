from fastapi import APIRouter

router = APIRouter(prefix="/builder", tags=["builder"])


@router.get("/tones")
def tones():
    """Return available tones for bot-building (temporary mock)."""
    return ["friendly", "professional", "concise-helpful"]


@router.post("/create")
def create_bot(payload: dict):
    """Mock create bot handler (for v1 smoke tests)."""
    return {"id": "bot-123", "status": "draft", "payload": payload}
