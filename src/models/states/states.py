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
    user_summary: str
    jd: JobDescription
    current_question: str
    is_curr_question_independent: bool
    current_response: str
    plan: Plan
    current_topic_id: str
    current_topic_question_count: int
    current_phase_name: str
    final_report: str