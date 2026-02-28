from typing import List, Optional, TypedDict
from pydantic import BaseModel, EmailStr, Field

from langchain_core.messages import BaseMessage

from .turn import Turn
from .phase_summary import PhaseSummary
from ..user_model import User
from ..jd_model import JobDescription
from ..plan_model import Plan


# class InterviewTurn(TypedDict):
#     question: BaseMessage
#     answer: str
#     metrics: dict


# class GlobalState(TypedDict):
#     session_id: str
#     current_user: User
#     current_jd: JobDescription
#     user_summary: str

#     recent_turns: List[InterviewTurn]
#     turn_count: int
#     max_turns: int
#     store_count: int

#     interview_phase: str
#     next_question: Optional[str]

#     final_report: Optional[str] = None


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