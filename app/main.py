from fastapi import FastAPI

app = FastAPI(title="AI Factory (experimental)", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}
# touch: 2025-09-14 15:24:56

# --- bots api wiring ---
from . import db
from .router_bots import router as bots_router
try:
    db.init_db()
except Exception as e:
    print("DB init failed:", e)
try:
    app.include_router(bots_router)
except Exception as e:
    print("Router include failed:", e)
