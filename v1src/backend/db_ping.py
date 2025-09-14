"""
Lightweight DB ping that *never* raises outwards.
Uses SQLAlchemy if available; otherwise returns {"db":"unknown"}.

Env:
  DATABASE_URL (e.g., postgresql+psycopg2://postgres:postgres@db:5432/postgres)
Fallback if unset: postgresql+psycopg2://postgres:postgres@db:5432/postgres
"""

from __future__ import annotations
import os


def ping_db():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@db:5432/postgres",
    )
    try:
        # Import lazily so missing deps don't kill app
        import sqlalchemy
        from sqlalchemy import text

        try:
            engine = sqlalchemy.create_engine(url, pool_pre_ping=True, pool_recycle=300)
        except Exception as e:
            return {
                "db": "error",
                "url": url,
                "stage": "create_engine",
                "error": str(e),
            }

        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"db": "ok", "driver": str(engine.dialect.name), "url": url}
        except Exception as e:
            return {"db": "error", "url": url, "stage": "connect/exec", "error": str(e)}
    except Exception as e:
        # SQLAlchemy not installed or import failed
        return {
            "db": "unknown",
            "url": url,
            "note": "sqlalchemy not available",
            "error": str(e),
        }
