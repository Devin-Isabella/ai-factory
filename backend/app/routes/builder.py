import os, json, re, time
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..db import get_db, get_current_user_optional
from ..models import Agent

router = APIRouter(prefix="/builder", tags=["builder"])

TONES = [
  "concise-helpful","friendly","professional","empathetic","motivational",
  "creative","analytical","critical","casual","humorous",
  "storyteller","teacherly","direct","inspirational","sarcastic"
]
HIDDEN_TONE = "silent"

DATA_DIR = os.environ.get("APP_DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)

def _bot_dir(bot_id:int)->str:
    p = os.path.join(DATA_DIR, "bots", str(bot_id)); os.makedirs(p, exist_ok=True); return p
def _meta_path(bot_id:int)->str: return os.path.join(_bot_dir(bot_id), "meta.json")
def _safety_path(bot_id:int)->str: return os.path.join(_bot_dir(bot_id), "safety.txt")

def _load_meta(bot_id:int)->Dict[str,Any]:
    try:
        with open(_meta_path(bot_id),"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
def _save_meta(bot_id:int, obj:Dict[str,Any])->None:
    mp = _meta_path(bot_id); tmp = mp + ".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, mp)
def _write_safety(bot_id:int, text:str)->None:
    with open(_safety_path(bot_id),"w",encoding="utf-8") as f: f.write(text or "")
def _read_safety(bot_id:int)->str:
    try:
        with open(_safety_path(bot_id),"r",encoding="utf-8") as f: return f.read()
    except Exception: return ""
def _now()->int: return int(time.time())

def _auto_name_from_text(text:str)->str:
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9\s&]", " ", t)
    words = [w for w in t.split() if len(w)>2]
    priority = ["calendar","reminder","reminders","schedule","planner","tasks","notes","report","summary","search","email","chat","qa","support","orders","inventory","docs"]
    picked = []
    for w in priority:
        if w in words and w not in picked: picked.append(w)
        if len(picked)>=3: break
    if not picked:
        for w in words:
            if w not in picked: picked.append(w)
            if len(picked)>=3: break
    label = (" ".join(picked) or "assistant")[:18].strip()
    return label or "assistant"

def _display_name_author(agent:Agent, meta:Dict[str,Any])->str:
    admin_name = meta.get("admin_name")
    creator_name = agent.name or ""
    return f"{admin_name} ({creator_name})" if admin_name else creator_name

def _ban_username(user):
    if not user: return
    nm = (user.get("name") or "")
    em = (user.get("email") or "")
    if re.search(r"devin", nm, re.IGNORECASE):
        if em.lower() != os.environ.get("ADMIN_EMAIL","").lower():
            raise HTTPException(status_code=400, detail="Usernames containing 'devin' are reserved")

@router.get("/tones")
def list_tones():
    return {"tones": TONES, "hidden": HIDDEN_TONE}

@router.post("/create")
def create_bot(
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    tone: str = Body("concise-helpful", embed=True),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    if not user: raise HTTPException(status_code=401, detail="auth required")
    _ban_username(user)
    if tone not in TONES: raise HTTPException(status_code=400, detail="invalid tone")
    a = Agent(); a.name = name; a.description = description or ""; a.tone_profile = tone; a.published = False; a.owner_id = user.get("id")
    db.add(a); db.commit(); db.refresh(a)
    meta = {"review_status":"draft","admin_name":None,"auto_name_admin":None,"submitted_at":None,"reviewed_at":None,"review_notes":None,"safety_score":None,"safety_rating":None}
    _save_meta(a.id, meta); _write_safety(a.id, "")
    return {"id": a.id, "status": meta["review_status"]}

@router.post("/save/{bot_id}")
def save_bot(
    bot_id:int,
    name: Optional[str] = Body(None, embed=True),
    description: Optional[str] = Body(None, embed=True),
    tone: Optional[str] = Body(None, embed=True),
    safety_text: Optional[str] = Body(None, embed=True),
    safety_score: Optional[int] = Body(None, embed=True),
    safety_rating: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    if not user: raise HTTPException(status_code=401, detail="auth required")
    _ban_username(user)
    a = db.query(Agent).filter(Agent.id==bot_id).first()
    if not a: raise HTTPException(status_code=404, detail="bot not found")
    if a.owner_id != user.get("id"): raise HTTPException(status_code=403, detail="not your bot")
    if name is not None: a.name = name
    if description is not None: a.description = description
    if tone is not None:
        if tone not in TONES: raise HTTPException(status_code=400, detail="invalid tone")
        a.tone_profile = tone
    db.commit()
    meta = _load_meta(bot_id)
    if safety_score is not None: meta["safety_score"] = int(safety_score)
    if safety_rating is not None: meta["safety_rating"] = safety_rating
    _save_meta(bot_id, meta)
    if safety_text is not None: _write_safety(bot_id, safety_text)
    return {"ok": True}

@router.post("/submit/{bot_id}")
def submit_bot(
    bot_id:int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    if not user: raise HTTPException(status_code=401, detail="auth required")
    _ban_username(user)
    a = db.query(Agent).filter(Agent.id==bot_id).first()
    if not a: raise HTTPException(status_code=404, detail="bot not found")
    if a.owner_id != user.get("id"): raise HTTPException(status_code=403, detail="not your bot")
    saf = _read_safety(bot_id)
    if not saf.strip(): raise HTTPException(status_code=400, detail="safety.txt required to submit")
    meta = _load_meta(bot_id)
    if not meta.get("auto_name_admin"):
        base = " ".join([a.name or "", a.description or "", saf or "", a.tone_profile or ""])
        meta["auto_name_admin"] = _auto_name_from_text(base)
    meta["review_status"] = "submitted"; meta["submitted_at"] = _now()
    _save_meta(bot_id, meta)
    return {"ok": True, "auto_name_admin": meta["auto_name_admin"]}

@router.get("/mine")
def my_bots(db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    if not user: raise HTTPException(status_code=401, detail="auth required")
    q = db.query(Agent).filter(Agent.owner_id==user.get("id")); items=[]
    for a in q.all():
        m = _load_meta(a.id)
        items.append({"id": a.id, "display_name": _display_name_author(a,m), "creator_name": a.name or "", "admin_name": m.get("admin_name"),
                      "review_status": m.get("review_status","draft"), "published": bool(a.published),
                      "tone": a.tone_profile or "", "safety_score": m.get("safety_score"), "safety_rating": m.get("safety_rating")})
    return {"items": items}
