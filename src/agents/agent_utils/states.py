from typing import TypedDict, Optional
from ...models.user_model import User
from ...models.jd_model import JobDescription

class GlobalState(TypedDict):
    session_id: str
    current_user: User
    current_jd: JobDescription
    final_report: Optional[str] = None
    user_summary: str 