from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from .util_model import Emp_Type,  Loc_Type, Salary



class JobDescription(BaseModel):
    job_title: str = Field(...)
    job_type: Emp_Type = Field(...)
    loc_type: Optional[Loc_Type] = None
    location: Optional[str] = ""
    salary: Optional[Salary] = None
    min_experience: float = Field(...)
    responsibilities: List[str] = Field(...)
    required_qualification: str = Field(...)
    required_skills: List[str] = Field(...)
    preferred_skills: Optional[List[str]] = []
    description: Optional[str] = ""

