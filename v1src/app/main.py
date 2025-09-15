from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Only mount static if it exists
if os.path.isdir("v1src/app/static"):
    app.mount("/static", StaticFiles(directory="v1src/app/static"), name="static")

# Import routers if present
try:
    from .bots import router as bots_router
    app.include_router(bots_router)
except Exception as e:
    print("⚠️ Skipping bots router:", e)

try:
    from .builder import router as builder_router
    app.include_router(builder_router)
except Exception as e:
    print("⚠️ Skipping builder router:", e)

try:
    from .powerrender import router as powerrender_router
    app.include_router(powerrender_router)
except Exception as e:
    print("⚠️ Skipping powerrender router:", e)
