from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import datetime, pathlib

# --- bot store bits ---
from . import db
from .router_bots import router as bots_router
from .router_store import router as store_router

app = FastAPI(title="AI Factory v1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"hello": "world"}

@app.get("/info")
def info():
    return {
        "name": "ai-factory",
        "version": "v1",
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# init the sqlite db
try:
    db.init_db()
except Exception as e:
    print("DB init failed:", e)

# mount static AFTER app exists
app.mount(
    "/static",
    StaticFiles(directory=str((pathlib.Path(__file__).parent / "static"))),
    name="static",
)

# include routers AFTER app exists
try:
    app.include_router(bots_router)    # /bots...
    app.include_router(store_router)   # /store (HTML)
except Exception as e:
    print("Router include failed:", e)
