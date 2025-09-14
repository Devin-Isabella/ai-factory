from fastapi import FastAPI

app = FastAPI(title="AI Factory", version="0.1.0")

@app.get("/health", summary="Health")
def health():
    return {"status": "ok"}

@app.get("/info", summary="Info")
def info():
    return {"name": "ai-factory-experimental", "env": "experimental"}
