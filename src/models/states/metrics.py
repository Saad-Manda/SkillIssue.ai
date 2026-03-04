from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

class Metrics(BaseModel):
    QAR: float
    TDS: float
    ACS: float
    SS: float
    CCS: float
    FARQ: float
    RFD: float
    RFD_flags: list[str]
    STAR_turn: float = 0.0            
    STAR_cumulative: float = 0.0 
    STAR_components: dict = {}