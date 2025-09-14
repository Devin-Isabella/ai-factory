from fastapi import APIRouter
import os
import platform
import time

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/stats")
def stats():
    return {
        "time": int(time.time()),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cwd": os.getcwd(),
        "env_admin_email": os.environ.get("ADMIN_EMAIL"),
    }


@router.get("/db")
def db_health():
    # Import lazily; if helper or dependencies missing, never crash
    try:
        from ..db_ping import ping_db

        return ping_db()
    except Exception as e:
        return {
            "db": "unknown",
            "note": "db_ping helper not available",
            "error": str(e),
        }
