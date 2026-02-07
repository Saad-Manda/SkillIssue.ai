from typing import List, Optional, TypedDict

from langchain_core.messages import BaseMessage

from ...models.jd_model import JobDescription
from ...models.user_model import User


class InterviewTurn(TypedDict):
    question: BaseMessage
    answer: str
    metrics: dict


class GlobalState(TypedDict):
    session_id: str
    current_user: User
    current_jd: JobDescription
    user_summary: str

    recent_turns: List[InterviewTurn]
    turn_count: int
    max_turns: int
    store_count: int

    interview_phase: str
    next_question: Optional[str]

    final_report: Optional[str] = None
