from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from sqlalchemy import Column, Float, Integer, DateTime, String, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

class Leadership(Base):
    __tablename__ = "leaderships"

    leadership_id = Column(String, primary_key=True, index=True)
    committee_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    skills_used = Column(ARRAY(String), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    user_id = Column(String, ForeignKey("users.user_id"))
    user = relationship("User", back_populates="leaderships")
