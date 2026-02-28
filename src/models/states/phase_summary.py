from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

class PhaseSummary(BaseModel):
    phase_summary_id: str
    phase_name: str
    summary: str