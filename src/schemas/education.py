from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Float, Integer, DateTime, String, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class Education(Base):
    __tablename__ = "educations"

    education_id = Column(String, primary_key=True, index=True)
    institute_name = Column(String, nullable=False)
    degree = Column(String, nullable=True)
    grade = Column(Float, nullable=False)
    courses = Column(ARRAY(String), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    user_id = Column(String, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="educations")