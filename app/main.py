from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/info")
async def info():
    return {"app": "ai-factory", "version": "0.1.0"}
