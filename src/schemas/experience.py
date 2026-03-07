from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Integer, DateTime, String, JSON, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class EmpType(Enum):
    PART_TIME = "part_time"
    FULL_TIME = "full_time"

class LocType(Enum):
    REMOTE = "remote"
    ONSITE = "onsite"

class Experience(Base):
    __tablename__ = "experiences"

    experience_id = Column(String, primary_key=True, index=True)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    emp_type = Column(Enum[EmpType], nullable=True)
    loc_type = Column(Enum[LocType], nullable=True)
    skills_used = Column(ARRAY(String), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    user_id = Column(String, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="experiences")