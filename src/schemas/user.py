from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, DateTime, String, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class User(Base):

    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, nullable=False, default=True
    name = Column(String, nullable=False)
    mobile = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    skills = Column(ARRAY(String), nullable=False)

    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    leaderships = relationship("Leadership", back_populates="user", cascade="all, delete-orphan")