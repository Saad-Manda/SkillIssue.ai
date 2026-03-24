from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .states.turn import Turn

class Interview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    user_id: str
    jd_id: str
    chat_history: List[Turn]