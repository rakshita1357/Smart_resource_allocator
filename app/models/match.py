from pydantic import BaseModel
from typing import Optional

class Match(BaseModel):
    id: Optional[str] = None
    volunteer_id: str
    need_id: str
    score: float
    status: str = "pending"
    # in process