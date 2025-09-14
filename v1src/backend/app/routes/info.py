from fastapi import APIRouter

router = APIRouter(prefix="/info", tags=["info"])


@router.get("/ping")
def ping():
    """Basic liveness check."""
    return {"status": "ok"}


@router.get("/version")
def version():
    """Return version metadata."""
    return {"version": "v1.0.0"}
