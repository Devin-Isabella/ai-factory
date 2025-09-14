from fastapi import FastAPI

app = FastAPI(title="AI Factory (experimental)", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}
# touch: 2025-09-14 15:24:56
