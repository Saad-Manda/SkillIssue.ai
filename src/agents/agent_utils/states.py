from typing import TypedDict, Optional, List
from ...models.user_model import User
from ...models.jd_model import JobDescription
from langchain_core.messages import BaseMessage


class InterviewTurn(TypedDict):
    question: str
    answer: str
    metrics: dict

class GlobalState(TypedDict):
    session_id: str
    current_user: User
    current_jd: JobDescription
    user_summary: str

    recent_turns: List[InterviewTurn]
    
    interview_phase: str
    next_question: Optional[str]
    chat_history: List[BaseMessage]

    final_report: Optional[str] = None
