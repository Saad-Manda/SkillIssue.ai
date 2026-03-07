from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db

from ..models.jd_model import JobDescription as JobDescriptionModel
from ..schemas.jd import JobDescription as JobDescriptionSchema
from ..controllers.job_description.get_jd import get_jd
from ..controllers.job_description.create_jd import create_jd
from ..controllers.job_description.delete_jd import delete_jd


router = APIRouter(prefix="/api/v1/jd", tags=["job_descriptions"])

@router.get("/{jd_id}", response_model=JobDescriptionModel)
async def get_jd_endpoint(jd_id: str, db: AsyncSession = Depends(get_db)):
    jd = await get_jd(db, jd_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description Not Found")
    return jd

@router.post("/", response_model=JobDescriptionModel)
async def create_jd_endpoint(jd_payload: dict, db: AsyncSession = Depends(get_db)):
    return await create_jd(db, jd_payload)

@router.delete("/{jd_id}")
async def delete_jd_endpoint(jd_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_jd(db, jd_id)