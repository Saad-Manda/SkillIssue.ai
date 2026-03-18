from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .experience_model import Experience
from .education_model import Education
from .project_model import Project
from .leadership_model import LeaderShip
from typing import List, Optional


class UserPublic(BaseModel):
    user_id: str
    email: EmailStr = Field(...)
    username: str = Field(...)
    is_active: bool = True

class User(UserPublic):
    model_config = ConfigDict(from_attributes=True)

    name: str
    hashed_password: str
    mobile: Optional[str] = ""
    github_url: Optional[str] = ""
    linkedin_url: Optional[str] = ""
    experiences: List[Experience] = []
    educations : List[Education] = []
    skills: List[str]
    projects: List[Project] = []
    leaderships: List[LeaderShip] = []
    
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

class SignupResponse(BaseModel):
    access_token: str
    signup_token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str