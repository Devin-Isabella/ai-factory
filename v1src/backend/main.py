from fastapi.responses import FileResponse
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Factory", version="0.1.0")

# CORS (open for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic health/info
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "app": "ai-factory",
        "cwd": os.getcwd(),
        "env": {
            k: v
            for k, v in os.environ.items()
            if k in ("DATABASE_URL", "PORT", "HOST", "PYTHONPATH")
        },
    }


# Mount /static if present
_here = os.path.dirname(__file__)
_static = os.path.join(_here, "static")
if os.path.isdir(_static):
    app.mount("/static", StaticFiles(directory=_static), name="static")


def _safe_import_and_include(module_path: str, attr_name: str = "router"):
    """
    Import module_path and include 'attr_name' if present.
    Returns True if a router was found and included, else False.
    Never raises.
    """
    try:
        mod = __import__(module_path, fromlist=["*"])
        r = getattr(mod, attr_name, None)
        if r is not None:
            app.include_router(r)
            return True
    except Exception:
        pass
    return False


# Always try to include the info router (if defined there too)
_safe_import_and_include("backend.routes.info", "router")

# Optional routers (ok if missing)
for mod in ("backend.routes.monitor", "backend.routes.builder"):
    _safe_import_and_include(mod, "router")

# OPS router may define any of these names; include all that exist
try:
    import backend.routes.ops as _ops

    for candidate in (
        "router",
        "ops_router",
        "logs_router",
        "status_router",
        "ops_logs_router",
        "ops_status_router",
    ):
        r = getattr(_ops, candidate, None)
        if r is not None:
            app.include_router(r)
except Exception:
    # ops module missing or failed to import: ignore
    pass

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("backend/app/static/index.html")

