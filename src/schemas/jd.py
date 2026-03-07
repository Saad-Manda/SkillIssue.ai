from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, DateTime, String, JSON, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class EmpType(Enum):
    PART_TIME = "part_time"
    FULL_TIME = "full_time"

class LocType(Enum):
    REMOTE = "remote"
    ONSITE = "onsite"

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    jd_id = Column(String, primary_key=True, index=True)
    job_title = Column(String, nullable=False)
    job_type = Column(Enum(EmpType), nullable=True)
    loc_type = Column(Enum(LocType), nullable=True)
    location = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    min_experience = Column(Float, nullable=False)
    responsibilities = Column(ARRAY(String), nullable=True)
    required_qualification = Column(String, nullable=False)
    required_skills = Column(ARRAY(String), nullable=True)
    preferred_skills = Column(ARRAY(String), nullable=True)
    description = Column(String, nullable=True)