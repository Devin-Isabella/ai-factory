from fastapi import FastAPI

app = FastAPI(title="AI Factory v1", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "AI Factory v1 is running"}

# --- appended by setup ---
from datetime import datetime
import os

STARTED_AT = globals().get("STARTED_AT") or datetime.utcnow()
VERSION = os.getenv("APP_VERSION", "v1")

@app.get("/info")
def info():
    """Basic service info for quick checks."""
    return {
        "name": "ai-factory",
        "version": VERSION,
        "started_at": STARTED_AT.isoformat() + "Z",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


# --- bots api wiring (added) ---
from . import db  # sqlite file at /app/data.db
from .router_bots import router as bots_router
try:
    db.init_db()
except Exception as e:
    print("DB init failed:", e)
try:
    app.include_router(bots_router)
except Exception as e:
    print("Router include failed:", e)
