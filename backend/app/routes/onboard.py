from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..db import SessionLocal
from ..models import Client

router = APIRouter()

class OnboardInput(BaseModel):
    name: str
    email: EmailStr

class OnboardResult(BaseModel):
    client_id: int
    client_code: str

def _code_for(n: int) -> str:
    # A0001, A0002, ... Z9999 then AA0001 ...
    # Simple base-26 letters for prefix + 4-digit pad.
    import string, math
    letters = string.ascii_uppercase
    seq = n
    s = ""
    while seq > 0:
        seq, r = divmod(seq-1, 26)
        s = letters[r] + s
    if not s:
        s = "A"
    return f"{s}{str(n).zfill(4)}"

@router.post("/onboard", response_model=OnboardResult)
async def onboard(data: OnboardInput):
    db = SessionLocal()
    try:
        # create row; let DB assign sequential id
        dummy = Client(code="PENDING", name=data.name, email=data.email)
        db.add(dummy)
        db.commit()
        db.refresh(dummy)
        code = _code_for(dummy.id)
        dummy.code = code
        db.add(dummy)
        db.commit()
        return {"client_id": dummy.id, "client_code": code}
    finally:
        db.close()
