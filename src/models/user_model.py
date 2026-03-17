from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .experience_model import Experience
from .education_model import Education
from .project_model import Project
from .leadership_model import LeaderShip
from typing import List, Optional


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    mobile: Optional[str] = ""
    github_url: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    experiences: List[Experience] = []
    educations : List[Education] = []
    skills: List[str]
    projects: List[Project] = []
    leaderships: List[LeaderShip] = []