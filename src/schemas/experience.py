from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Integer, DateTime, String, JSON, Text, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class EmpType(str, Enum):
    part_time = "part_time"
    full_time = "full_time"

class LocType(str, Enum):
    remote = "remote"
    onsite = "onsite"

class Experience(Base):
    __tablename__ = "experiences"

    experience_id = Column(String, primary_key=True, index=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    emp_type = Column(SQLEnum(EmpType, native_enum=False, validate_strings=True), nullable=True)
    loc_type = Column(SQLEnum(LocType, native_enum=False, validate_strings=True), nullable=True)
    skills_used = Column(ARRAY(String), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    user_id = Column(String, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="experiences")