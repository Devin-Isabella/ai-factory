import datetime as dt
from sqlalchemy import Integer, String, Float, Boolean, JSON, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .db import Base

# ---------------- Agent ----------------
class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(String(1000), default="")
    category: Mapped[str] = mapped_column(String(80), index=True)

    # Library card (Step 18)
    tone_profile: Mapped[str] = mapped_column(String(400), default="")
    safety_rating: Mapped[str] = mapped_column(String(16), default="")
    safety_score: Mapped[float] = mapped_column(Numeric, nullable=True)
    lineage_display: Mapped[str] = mapped_column(String(400), default="")
    last_safety_check: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_cost: Mapped[float] = mapped_column(Numeric, nullable=True)

    # Ownership / publish / lineage
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('agents.id'), nullable=True, index=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Misc spec (MVP)
    spec: Mapped[dict] = mapped_column(JSON, default=dict)

    # Legacy placeholders (ok to keep)
    ethics_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

# --------------- InteractionLog ---------------
class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    prompt: Mapped[str] = mapped_column(String(8000))
    response: Mapped[str] = mapped_column(String(16000))
    user_sentiment_before: Mapped[str] = mapped_column(String(16), default="neutral")
    user_sentiment_after: Mapped[str] = mapped_column(String(16), default="neutral")
    usefulness_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

# --------------- AuditLog (Step 23) ---------------
class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64))
    actor_user_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    bot_id: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# --------------- Client (compat for legacy imports) ---------------
class Client(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    name: Mapped[str] = mapped_column(String(120), default="")
    role: Mapped[str] = mapped_column(String(32), default="owner")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
