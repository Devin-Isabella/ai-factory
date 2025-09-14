import sqlite3, threading, time
from pathlib import Path

_DB_FILE = Path(__file__).resolve().parent.parent / "data.db"
_LOCK = threading.Lock()

def _connect():
    # check_same_thread=False so FastAPI worker threads can share the same connection via our lock
    return sqlite3.connect(_DB_FILE, check_same_thread=False)

def init_db():
    with _LOCK:
        con = _connect()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS bots(
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            con.commit()
        finally:
            con.close()

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def list_bots():
    with _LOCK:
        con = _connect()
        try:
            cur = con.execute("SELECT id,name,description,status,created_at,updated_at FROM bots ORDER BY created_at DESC")
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols,row)) for row in cur.fetchall()]
        finally:
            con.close()

def get_bot(bot_id: str):
    with _LOCK:
        con = _connect()
        try:
            cur = con.execute("SELECT id,name,description,status,created_at,updated_at FROM bots WHERE id=?", (bot_id,))
            row = cur.fetchone()
            if not row: return None
            cols = [c[0] for c in cur.description]
            return dict(zip(cols,row))
        finally:
            con.close()

def upsert_bot(bot: dict):
    with _LOCK:
        con = _connect()
        try:
            existing = con.execute("SELECT 1 FROM bots WHERE id=?", (bot["id"],)).fetchone()
            if existing:
                con.execute("""
                    UPDATE bots SET name=?, description=?, status=?, updated_at=?
                    WHERE id=?
                """, (bot["name"], bot.get("description",""), bot.get("status","draft"), now_iso(), bot["id"]))
            else:
                con.execute("""
                    INSERT INTO bots(id,name,description,status,created_at,updated_at)
                    VALUES(?,?,?,?,?,?)
                """, (bot["id"], bot["name"], bot.get("description",""), bot.get("status","draft"), now_iso(), now_iso()))
            con.commit()
        finally:
            con.close()

def delete_bot(bot_id: str):
    with _LOCK:
        con = _connect()
        try:
            cur = con.execute("DELETE FROM bots WHERE id=?", (bot_id,))
            con.commit()
            return cur.rowcount
        finally:
            con.close()
