from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status

from ..models.interview_model import Interview


from ..controllers.interview.get_all_interviews import get_all_interviews
from ..controllers.interview.get_interview import get_interview
from ..controllers.interview.store_interview import add_interview
from ..controllers.interview.delete_interview import delete_interview

router = APIRouter(prefix="/api/v1/interview", tags=["interviews"])

@router.get("/", response_model=List[dict])
async def get_all_interviews_endpoint():
    interviews = await get_all_interviews()
    return interviews

@router.get("/{interview_id}", response_model=dict)
async def get_interview_endpoint(interview_id: str):
    interview = await get_interview(interview_id=interview_id)
    return interview

@router.post("/", response_model=dict)
async def store_interview_endpoint(interview_payload: Interview):
    interview = await add_interview(interview_payload)
    return interview

@router.delete("/{interview_id}", response_model=dict)
async def delete_interview_endpoint(interview_id: str):
    interview = await delete_interview(interview_id)
    return interview