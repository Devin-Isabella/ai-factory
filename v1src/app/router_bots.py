from fastapi import APIRouter, HTTPException
from typing import List
from .models import BotIn, BotOut
from . import db

router = APIRouter(prefix="/bots", tags=["bots"])

@router.get("", response_model=List[BotOut])
def list_bots():
    return db.list_bots()

@router.get("/{bot_id}", response_model=BotOut)
def get_bot(bot_id: str):
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(404, "bot not found")
    return bot

@router.post("", response_model=BotOut)
def create_bot(payload: BotIn):
    if db.get_bot(payload.id):
        raise HTTPException(409, "bot id already exists")
    db.upsert_bot(payload.model_dump())
    return db.get_bot(payload.id)

@router.put("/{bot_id}", response_model=BotOut)
def replace_bot(bot_id: str, payload: BotIn):
    if bot_id != payload.id:
        raise HTTPException(400, "bot_id must match payload.id")
    db.upsert_bot(payload.model_dump())
    return db.get_bot(bot_id)

@router.patch("/{bot_id}", response_model=BotOut)
def patch_bot(bot_id: str, payload: BotIn):
    existing = db.get_bot(bot_id)
    if not existing:
        raise HTTPException(404, "bot not found")
    merged = {
        "id": bot_id,
        "name": payload.name or existing["name"],
        "description": payload.description if payload.description is not None else existing["description"],
        "status": payload.status or existing["status"],
    }
    db.upsert_bot(merged)
    return db.get_bot(bot_id)

@router.delete("/{bot_id}")
def delete_bot(bot_id: str):
    deleted = db.delete_bot(bot_id)
    if not deleted:
        raise HTTPException(404, "bot not found")
    return {"deleted": bot_id}

@router.post("/{bot_id}/deploy", response_model=BotOut)
def deploy_bot(bot_id: str):
    bot = db.get_bot(bot_id)
    if not bot:
        raise HTTPException(404, "bot not found")
    bot["status"] = "active"
    db.upsert_bot(bot)
    return db.get_bot(bot_id)
