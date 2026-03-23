from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

from .util_model import Emp_Type,  Loc_Type


class Experience(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    experience_id: Optional[str] = None
    role: str = Field(...)
    company: str = Field(...)
    emp_type: Emp_Type = Field(...)
    skills_used: Optional[List[str]] = []
    start_date: date = Field(...)
    end_date: date = date.today()
    loc_type: Optional[Loc_Type] = None
    location: Optional[str] = ""
    description: Optional[str] = ""
