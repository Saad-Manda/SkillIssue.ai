from enum import Enum
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class Emp_Type(str, Enum):
    part_time: "part_time"
    full_time: "full_time"

class Loc_Type(str, Enum):
    remote: "remote"
    onsite: "onsite"

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
    


