from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .states.turn import Turn

class Interview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    _id: str
    session_id: str
    user_id: str
    jd_id: str
    report: str
    conducted_on: date
    chat_history: List[Turn]