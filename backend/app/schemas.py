from pydantic import BaseModel
from typing import Optional

class AgentCard(BaseModel):
    id: int
    name: str
    description: str
    category: str
    published: bool
    tone_profile: Optional[str] = ""
    safety_rating: Optional[str] = ""
    safety_score: Optional[float] = None
    lineage_display: Optional[str] = ""
    last_safety_check: Optional[str] = None
    usage_cost: Optional[float] = None
