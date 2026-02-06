from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from .util_model import Emp_Type,  Loc_Type


class Experience(BaseModel):
    role: str = Field(...)
    company: str = Field(...)
    emp_type: Emp_Type = Field(...)
    skills_used: Optional[List[str]] = []
    start_date: date = Field(...)
    end_date: date = date.today()
    loc_type: Optional[Loc_Type] = None
    location: Optional[str] = ""
    decription: Optional[str] = ""
    


