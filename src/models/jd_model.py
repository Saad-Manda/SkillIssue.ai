from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .util_model import Emp_Type,  Loc_Type, Salary



class JobDescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jd_id: Optional[str] = None
    job_title: str
    job_type: Emp_Type
    loc_type: Optional[Loc_Type] = None
    location: Optional[str] = ""
    salary: Optional[float] = None
    min_experience: float
    responsibilities: List[str]
    required_qualification: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    description: Optional[str] = ""