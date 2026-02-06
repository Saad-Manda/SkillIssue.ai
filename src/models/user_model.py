from pydantic import BaseModel, EmailStr, Field
from .experience_model import Experience
from .education_model import Education
from .project_model import Project
from leadership_model import LeaderShip
from typing import List, Optional


class User(BaseModel):
    id: str
    name: str = Field(...)
    email: Optional[EmailStr]
    mobile: Optional[str] = ""
    github_url: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    experience: Optional[Experience] = None
    education : Education = Field(...)
    skills: List[str] = Field(...)
    projects: Optional[Project]
    leadership: Optional[LeaderShip]
