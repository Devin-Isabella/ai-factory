from fastapi import APIRouter, Body, HTTPException

router = APIRouter(prefix="/builder", tags=["builder"])

TONES = [
    "concise-helpful",
    "friendly",
    "professional",
    "empathetic",
    "motivational",
    "creative",
    "analytical",
    "critical",
    "casual",
    "humorous",
    "storyteller",
    "teacherly",
    "direct",
    "inspirational",
    "sarcastic",
]


@router.get("/tones")
def list_tones():
    return {"tones": TONES}


@router.post("/create")
def create_bot(
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    tone: str = Body("concise-helpful", embed=True),
):
    if tone not in TONES:
        raise HTTPException(status_code=400, detail="invalid tone")
    # Fake ID so the UI flow can proceed before DB is added
    return {
        "id": 1,
        "name": name,
        "description": description,
        "tone": tone,
        "status": "draft (stub)",
    }
