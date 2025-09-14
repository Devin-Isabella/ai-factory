from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginIn(BaseModel):
    email: str
    name: str | None = None

class LoginOut(BaseModel):
    token: str
    user: dict

@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn):
    # Minimal demo token (stateless). Your real auth can replace this later.
    token = "demo-owner-token"
    return {"token": token, "user": {"email": payload.email, "name": payload.name or ""}}
