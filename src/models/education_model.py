from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class Education(BaseModel):
    institute_name: str = Field(...)
    degree: str = Field(...)
    grade: float = Field(...)
    courses: Optional[List[str]] = []
    start_date: Optional[date]
    end_date: Optional[date]
    
