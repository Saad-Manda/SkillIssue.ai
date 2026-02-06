from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class LeaderShip(BaseModel):
    commitee_name: str = Field(...)
    position: str = Field(...)
    skills_used: Optional[List[str]] = []
    description: Optional[str] = ""
    start_date: Optional[date]
    end_date: Optional[date]
