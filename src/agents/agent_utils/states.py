from typing import TypedDict
from ...models.user_model import User

class SummarizerAgentState(TypedDict):
    user: User
    summary: str
