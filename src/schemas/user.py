from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, DateTime, String, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class User(Base):

    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(EmailStr, nullable=True)
    mobile = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    skills = Column(ARRAY(String), nullable=False)

    # experience
    # education
    # project
    # leadership