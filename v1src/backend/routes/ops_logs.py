from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="/ops", tags=["ops"])

LOG_PATH = Path("/logs/backend.log")
STATUS_PATH = Path("/logs/status.json")


@router.get("/logs")
def get_logs(lines: int = 200):
    try:
        if not LOG_PATH.exists():
            return {"note": "log file not found", "path": str(LOG_PATH)}
        # clamp lines
        n = max(1, min(int(lines), 2000))
        with LOG_PATH.open("r", encoding="utf-8", errors="ignore") as f:
            buf = f.readlines()[-n:]
        return {"path": str(LOG_PATH), "lines": len(buf), "content": "".join(buf)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def get_status():
    if not STATUS_PATH.exists():
        return {"status": "unknown", "path": str(STATUS_PATH)}
    try:
        txt = STATUS_PATH.read_text(encoding="utf-8", errors="ignore")
        return {"status": "ok", "raw": txt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
