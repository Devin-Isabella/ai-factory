from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/store")
def store():
    here = Path(__file__).resolve().parent
    page = here / "static" / "store.html"
    return FileResponse(str(page))
