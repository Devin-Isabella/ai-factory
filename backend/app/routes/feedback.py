from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db, get_current_user_optional

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackIn(BaseModel):
    email: str | None = None
    message: str = Field(min_length=3, max_length=4000)

@router.post("")
def submit(fb: FeedbackIn, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    q = text('INSERT INTO public.feedbacks(email, message) VALUES (:email, :message) RETURNING id')
    rid = db.execute(q, {"email": fb.email or (user["email"] if user else None), "message": fb.message}).scalar()
    db.commit()
    return {"id": int(rid)}
