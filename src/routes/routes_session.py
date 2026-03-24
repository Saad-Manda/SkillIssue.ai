import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers.session.create_report import get_report
from ..controllers.session.send_answer import submit_answer
from ..controllers.session.start_session import start_session
from ..database import get_db

router = APIRouter(prefix="/api/v1/interview", tags=["interviews"])
logger = logging.getLogger(__name__)


class SubmitAnswerRequest(BaseModel):
    answer: str


@router.get("/user/{user_id}/jd/{jd_id}/length/{interview_length}")
async def start_session_endpoint(
    user_id: str, jd_id: str, interview_length: str, db: AsyncSession = Depends(get_db)
):
    logger.info(
        "start_session_endpoint called for user_id=%s jd_id=%s interview_length=%s",
        user_id,
        jd_id,
        interview_length,
    )
    session_id, state, chat, turn_count, store_count = await start_session(
        user_id, jd_id, interview_length, db
    )
    logger.info("start_session_endpoint succeeded for session_id=%s", session_id)
    return {
        "session_id": session_id,
        "current_question": state.current_question,
        "current_phase_name": state.current_phase_name,
        "current_topic_id": state.current_topic_id,
        "chat": chat,
    }


@router.post("/{session_id}/answer")
async def submit_answer_endpoint(session_id: str, payload: SubmitAnswerRequest):
    logger.info("submit_answer_endpoint called for session_id=%s", session_id)
    state, chat, turn_count, store_count = submit_answer(
        session_id=session_id,
        answer=payload.answer,
    )
    logger.info(
        "submit_answer_endpoint succeeded for session_id=%s turn_count=%s",
        session_id,
        turn_count,
    )
    return {
        "session_id": session_id,
        "current_question": state.current_question,
        "current_phase_name": state.current_phase_name,
        "current_topic_id": state.current_topic_id,
        "turn_count": turn_count,
        "store_count": store_count,
        "chat": chat,
    }


@router.get("/{session_id}/report")
async def get_report_endpoint(session_id: str):
    logger.info("get_report_endpoint called for session_id=%s", session_id)
    report, state = get_report(session_id)
    logger.info("get_report_endpoint completed for session_id=%s", session_id)
    return {"report": report}