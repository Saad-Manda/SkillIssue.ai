import logging
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.user import User as UserSchema
from ..job_description.get_jd import get_jd
from ..user_profile.get_user_profile import get_user_profile
from .utils import _build_initial_state, _parse_json, _run_graph

logger = logging.getLogger(__name__)


async def start_session(
    user_id: str, jd_id: str, interview_length: str, db: AsyncSession
):
    logger.info(
        "start_session controller called for user_id=%s jd_id=%s interview_length=%s",
        user_id,
        jd_id,
        interview_length,
    )
    user = await get_user_profile(db, user_id)
    jd = await get_jd(db, jd_id)

    if not user:
        logger.warning(
            "start_session controller user not found for user_id=%s", user_id
        )
        raise HTTPException(status_code=404, detail="User not found")
    if not jd:
        logger.warning("start_session controller jd not found for jd_id=%s", jd_id)
        raise HTTPException(status_code=404, detail="Job Description not found")

    session_id = str(uuid4())
    logger.info("start_session controller created session_id=%s", session_id)

    initial_state = _build_initial_state(session_id, user, jd, interview_length)
    state = _run_graph(initial_state, resume=False)

    chat = []
    if state.current_question:
        chat.append({"role": "assistant", "content": state.current_question})

    turn_count = 0
    store_count = 1 if chat else 0

    logger.info("start_session controller succeeded for session_id=%s", session_id)
    return session_id, state, chat, turn_count, store_count
