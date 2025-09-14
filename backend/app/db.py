import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# DATABASE_URL example: postgresql+psycopg://ai_factory:ai_factory@db:5432/ai_factory
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://ai_factory:ai_factory@db:5432/ai_factory")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
Base = declarative_base()

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Minimal auth helpers for dependencies used by routes ---
from fastapi import Header, HTTPException  # added by fix script

def _parse_bearer(authorization: str | None):
    if not authorization:
        return None
    lower = authorization.lower()
    if lower.startswith("bearer "):
        return authorization[7:].strip()
    return None

def get_current_user(authorization: str = Header(None)):
    """
    Strict: requires Bearer token and returns a user dict.
    MVP: trust any token and map to owner user (id=1).
    """
    token = _parse_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    # TODO: validate token → user lookup
    return {"id": 1, "email": "owner@example.com"}

def get_current_user_optional(authorization: str = Header(None)):
    """
    Lenient: returns None when no token; else a user dict.
    """
    token = _parse_bearer(authorization)
    if not token:
        return None
    # TODO: validate token → user lookup
    return {"id": 1, "email": "owner@example.com"}

