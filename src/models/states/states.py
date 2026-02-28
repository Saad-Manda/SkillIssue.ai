from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

from langchain_core.messages import BaseMessage

from .turn import Turn
from .phase_summary import PhaseSummary
from ..user_model import User
from ..jd_model import JobDescription
from ..plan_model import Plan


class SessionState(BaseModel):
    session_id: str
    chat_history: List[Turn]
    phasewise_summary: List[PhaseSummary]


class SystemState(BaseModel):
    session_id: str
    user: User
    jd: JobDescription
    current_question: str
    current_response: str
    plan: Plan
    current_phase_name: str
    final_report: str