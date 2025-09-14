from fastapi import APIRouter
import psutil

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/system")
def system_metrics():
    """Returns basic CPU and memory usage stats."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory": psutil.virtual_memory()._asdict(),
    }
