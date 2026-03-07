from uuid import uuid4
from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..user_profile.get_user_profile import get_user_profile
from ..job_description.get_jd import get_jd
from ...schemas.user import User as UserSchema
from .utils import _parse_json, _build_initial_state, _run_graph


def start_session(user_id: str, jd_id: str, interview_length: str, db: AsyncSession):
    try:
        user = get_user_profile(db, user_id)
        jd = get_jd(db, jd_id)
    except Exception as e:
        return {"error": f"Failed to Fetch Credentials {e}"}

    session_id = str(uuid4())
    print(f"[start_session] created session_id={session_id!r}")

    initial_state = _build_initial_state(session_id, user, jd, interview_length)
    state = _run_graph(initial_state, resume=False)

    chat = []
    if state.current_question:
        chat.append({"role": "assistant", "content": state.current_question})

    turn_count = 0
    store_count = 1 if chat else 0

    return session_id, state, chat, turn_count, store_count



