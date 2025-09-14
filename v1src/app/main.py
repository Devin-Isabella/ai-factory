from fastapi import FastAPI
import os, datetime

# --- bot store bits ---
from . import db
from .router_bots import router as bots_router

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

# init the sqlite db and include the /bots router
try:
    db.init_db()
except Exception as e:
    print("DB init failed:", e)

try:
    app.include_router(bots_router)  # -> /bots, /bots/{id}, /bots/{id}/deploy
except Exception as e:
    print("Router include failed:", e)
