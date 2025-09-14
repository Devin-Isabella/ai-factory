from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

def _asset(path: str) -> str:
    here = Path(__file__).parent
    static_dir = here / "static"
    return str(static_dir / path)

@router.get("/store", include_in_schema=False)
def store_page():
    return FileResponse(_asset("store.html"))
