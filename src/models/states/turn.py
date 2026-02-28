from typing import Any, List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

from .metrics import Metrics

class Turn(BaseModel):
    chat_id: str
    question: str
    response: str
    metrics: List[Metrics]
    phase_name: str
    topic_id: str