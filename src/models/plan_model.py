from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

class Topic(BaseModel):
    topic_id: str
    topic: str
    source: str
    weight: float

class Phase(BaseModel):
    phase_id: str
    name: str
    objective: str
    weight: float
    topics: List[Topic]

class Plan(BaseModel):
    phase: List[Phase]