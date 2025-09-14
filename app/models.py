from pydantic import BaseModel, Field
from typing import Optional

class BotIn(BaseModel):
    id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9._-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    status: Optional[str] = "draft"  # draft|active|disabled

class BotOut(BotIn):
    created_at: str
    updated_at: str
