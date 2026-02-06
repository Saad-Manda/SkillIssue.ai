from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class Project(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    skills_used: List[str] = Field(...)
    github_url: Optional[str] = ""
    deployed_url: Optional[str] = ""
    
    