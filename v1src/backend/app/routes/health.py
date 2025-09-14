from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check():
    """Health endpoint used by probes (Cloudflare, Docker, etc.)."""
    return {"status": "ok"}
