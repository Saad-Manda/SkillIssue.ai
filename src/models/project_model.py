from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(...)
    description: str = Field(...)
    skills_used: List[str] = Field(...)
    github_url: Optional[str] = ""
    deployed_url: Optional[str] = ""