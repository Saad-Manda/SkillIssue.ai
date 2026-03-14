from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LeaderShip(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    committee_name: str = Field(...)
    position: str = Field(...)
    skills_used: Optional[List[str]] = []
    description: Optional[str] = ""
    start_date: Optional[date]
    end_date: Optional[date]
