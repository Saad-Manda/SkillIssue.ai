from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db

from ..controllers.session.start_session import start_session
from ..controllers.session.send_answer import submit_answer
from ..controllers.session.create_report import get_report

router = APIRouter(prefix="/api/v1/interview", tags=["interviews"])

@router.get("/user/{user_id}/jd/{jd_id}/length/{length}")
async def start_session_endpoint(user_id: str, jd_id: str, interview_length: str, db: AsyncSession = Depends(get_db)):
    session_id, state, chat, turn_count, store_count = await start_session(user_id, jd_id, interview_length, db)
    return {
        "session_id": session_id
    }

# @router.post("/{session_id}")
# async def submit_answer()