import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..controllers.session.create_report import get_report
from ..controllers.session.send_answer import submit_answer
from ..controllers.session.start_session import start_session
from ..database import get_db

router = APIRouter(prefix="/api/v1/session", tags=["sessions"])
logger = logging.getLogger(__name__)


def get_topic_name(plan, topic_id: str) -> str:
    if not plan or not getattr(plan, "phase", None):
        return topic_id
    for phase in plan.phase:
        if not getattr(phase, "topics", None):
            continue
        for topic in phase.topics:
            if topic.topic_id == topic_id:
                return topic.topic
    return topic_id


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
        "current_topic_name": state.current_topic_name or get_topic_name(state.plan, state.current_topic_id),
        "chat": chat,
    }


@router.post("/{session_id}/answer")
async def submit_answer_endpoint(session_id: str, payload: SubmitAnswerRequest):
    logger.info("submit_answer_endpoint called for session_id=%s", session_id)
    state, chat, turn_count, store_count, interview_complete = await run_in_threadpool(
        submit_answer,
        session_id=session_id,
        answer=payload.answer,
    )
    logger.info(
        "submit_answer_endpoint succeeded for session_id=%s turn_count=%s interview_complete=%s",
        session_id,
        turn_count,
        interview_complete,
    )
    return {
        "session_id": session_id,
        "current_question": state.current_question,
        "interview_complete": interview_complete,
        "report": state.final_report if interview_complete else None,
        "current_phase_name": state.current_phase_name,
        "current_topic_id": state.current_topic_id,
        "current_topic_name": state.current_topic_name or get_topic_name(state.plan, state.current_topic_id),
        "turn_count": turn_count,
        "store_count": store_count,
        "chat": chat,
    }


@router.get("/{session_id}/report")
async def get_report_endpoint(session_id: str):
    logger.info("get_report_endpoint called for session_id=%s", session_id)
    report, state = await get_report(session_id)
    logger.info("get_report_endpoint completed for session_id=%s", session_id)
    return {"report": report}


@router.get("/{session_id}/events")
async def stream_session_events(session_id: str, request: Request):
    async def event_stream():
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = client.pubsub()
        await pubsub.subscribe(f"session:{session_id}:events")
        try:
            while True:
                if await request.is_disconnected():
                    break
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=15.0)
                if msg and msg["type"] == "message":
                    yield f"data: {msg['data']}\n\n"
                else:
                    yield ": keepalive\n\n"
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()
            await client.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )