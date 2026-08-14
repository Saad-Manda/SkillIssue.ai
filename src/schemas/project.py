from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Float, Integer, DateTime, String, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    skills_used = Column(ARRAY(String), nullable=True)
    github_url = Column(String, nullable=True)
    deployed_url = Column(String, nullable=True)

    user_id = Column(String, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="projects")