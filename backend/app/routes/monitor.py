from fastapi import APIRouter, Depends
try:
    import psutil
    HAS_PSUTIL=True
except Exception:
    HAS_PSUTIL=False

# optional DB health
try:
    from ..db import get_db
    from sqlalchemy.orm import Session
    HAS_DB=True
except Exception:
    HAS_DB=False
    def get_db(): 
        yield None
        return

router = APIRouter(prefix="/monitor", tags=["monitor"])

@router.get("/stats")
def stats():
    if not HAS_PSUTIL:
        return {"cpu": None, "mem": None, "note": "psutil not installed"}
    cpu = psutil.cpu_percent(interval=0.0)
    mem = psutil.virtual_memory()._asdict()
    return {"cpu": cpu, "mem": mem}

@router.get("/db")
def db_health(db: 'Session' = Depends(get_db)):
    if not HAS_DB or db is None:
        return {"db": "unknown"}
    try:
        db.execute("SELECT 1")
        return {"db": "ok"}
    except Exception:
        return {"db": "error"}
