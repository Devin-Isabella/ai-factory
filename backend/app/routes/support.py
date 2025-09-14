from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
import httpx

from ..db import SessionLocal
from ..models import Agent, InteractionLog
from ..llm_adapter import invoke_openai

router = APIRouter()

class AskInput(BaseModel):
    agent_id: int
    question: str

class AskOutput(BaseModel):
    # Avoid Pydantic protected name warning (model_)
    model_config = ConfigDict(protected_namespaces=())
    answer: str
    model_name: str

@router.post("/support/ask", response_model=AskOutput)
async def ask(payload: AskInput):
    db: Session = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == payload.agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Safe default: your stack has used gpt-4o-mini successfully
        model = ((agent.spec or {}).get("primary_model")) or "gpt-4o-mini"

        system_prompt = "Be brief and helpful. If you don't know, say so in one short sentence."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.question},
        ]

        try:
            reply = await invoke_openai(
                model=model,
                messages=messages,
                max_tokens=120,
                temperature=0.3,
            )
        except httpx.HTTPStatusError as e:
            # Bubble up the real API error text so we can see what's wrong
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

        # Best-effort log
        try:
            log = InteractionLog(
                agent_id=agent.id,
                prompt=payload.question,
                response=reply,
                user_sentiment_before="neutral",
                user_sentiment_after="neutral",
                usefulness_score=0.0,
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()  # don’t break the endpoint if logging fails

        return AskOutput(answer=reply, model_name=model)
    finally:
        db.close()
