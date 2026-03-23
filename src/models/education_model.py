from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class Education(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    education_id: Optional[str] = None
    institute_name: str = Field(...)
    degree: str = Field(...)
    grade: float = Field(...)
    courses: Optional[List[str]] = []
    start_date: Optional[date]
    end_date: Optional[date]
