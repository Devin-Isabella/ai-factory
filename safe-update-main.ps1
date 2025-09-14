# safe-update-main.ps1
# Kills Notepad locks, writes full main.py, rebuilds backend, sanity checks.

$ErrorActionPreference = "Stop"
$mainPath = "backend\app\main.py"

# 1) Kill Notepad if it's locking the file
Get-Process notepad -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 2) Write full, dict-compatible main.py
@'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx

from .db import SessionLocal, engine, Base
from .models import Agent, InteractionLog
from .brain import build_agent_spec
from .checker import run_checker
from .llm_adapter import invoke_openai

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Factory")

# Allow local testing via curl, Postman, browser, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    name: str
    description: str
    category: str
    tone: str = "neutral"
    target: str = "web"
    budget_guard: str = "balanced"
    needs: list[str] = []

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/agents")
async def create_agent(req: AgentRequest):
    db: Session = SessionLocal()
    try:
        spec = build_agent_spec(req.dict())
        agent = Agent(
            name=req.name,
            description=req.description,
            category=req.category,
            spec=spec,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    finally:
        db.close()

@app.get("/agents")
async def list_agents():
    db: Session = SessionLocal()
    try:
        agents = db.execute(select(Agent)).scalars().all()
        return agents
    finally:
        db.close()

@app.post("/agents/{agent_id}/test")
async def test_agent(agent_id: int):
    db: Session = SessionLocal()
    try:
        agent = db.get(Agent, agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        prompt = f"Run a quick ethics + trust check for agent {agent.name}"
        try:
            reply = await invoke_openai(
                prompt,
                model=agent.spec["routing"]["primary"],
                max_tokens=agent.spec["limits"]["max_output_tokens"]
            )
        except httpx.HTTPStatusError as e:
            # Retry on 429 or escalate to first fallback
            if e.response.status_code == 429:
                fallback = agent.spec["routing"].get("escalation", [])
                if fallback:
                    reply = await invoke_openai(
                        prompt,
                        model=fallback[0],
                        max_tokens=agent.spec["limits"]["max_output_tokens"]
                    )
                else:
                    raise HTTPException(status_code=503, detail="Quota exceeded and no fallback available")
            else:
                raise

        # checker.py returns dict: {"passed": bool, "trust_score": float, ...}
        result = run_checker({"quick_check": reply})
        passed = bool(result.get("passed", False))
        trust_score = float(result.get("trust_score", 0.0))

        agent.ethics_passed = passed
        agent.trust_score = trust_score
        db.add(agent)
        db.commit()
        db.refresh(agent)

        return {"passed": passed, "trust_score": trust_score, "details": result}
    finally:
        db.close()

class InvokeRequest(BaseModel):
    agent_id: int
    message: str

@app.post("/invoke")
async def invoke(req: InvokeRequest):
    db: Session = SessionLocal()
    try:
        agent = db.get(Agent, req.agent_id)
        if not agent or not agent.ethics_passed:
            raise HTTPException(status_code=400, detail="Agent not found or not approved")

        try:
            reply = await invoke_openai(
                req.message,
                model=agent.spec["routing"]["primary"],
                max_tokens=agent.spec["limits"]["max_output_tokens"]
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                fallback = agent.spec["routing"].get("escalation", [])
                if fallback:
                    reply = await invoke_openai(
                        req.message,
                        model=fallback[0],
                        max_tokens=agent.spec["limits"]["max_output_tokens"]
                    )
                else:
                    raise HTTPException(status_code=503, detail="Quota exceeded and no fallback available")
            else:
                raise

        # Log interaction
        log = InteractionLog(
            agent_id=req.agent_id,
            prompt=req.message,
            response=reply,
            user_sentiment_before="neutral",
            user_sentiment_after="neutral",
            usefulness_score=0.0
        )
        db.add(log)
        db.commit()

        return {"reply": reply, "model_used": agent.spec["routing"]["primary"]}
    finally:
        db.close()
'@ | Set-Content -Path $mainPath -Encoding UTF8 -Force

Write-Host "✅ Wrote $mainPath"

# 3) Rebuild backend
docker compose up -d --force-recreate --build backend | Out-Host

Start-Sleep -Seconds 2
Write-Host "`n📜 Backend logs (last 80 lines):"
docker logs ai_factory_backend --tail 80 | Out-Host

# 4) Quick sanity checks
Write-Host "`n🔎 Health:"
try { Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get | Out-Host } catch { $_ | Out-String | Write-Host }

Write-Host "`n📋 Agents:"
try { Invoke-RestMethod -Uri "http://localhost:8000/agents" -Method Get | Out-Host } catch { $_ | Out-String | Write-Host }
