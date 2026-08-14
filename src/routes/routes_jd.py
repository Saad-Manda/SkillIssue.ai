import logging

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers.job_description.create_jd import create_jd
from ..controllers.job_description.delete_jd import delete_jd
from ..controllers.job_description.get_jd import get_jd
from ..database import get_db
from ..models.jd_model import JobDescription as JobDescriptionModel
from ..schemas.jd import JobDescription as JobDescriptionSchema

router = APIRouter(prefix="/api/v1/jd", tags=["job_descriptions"])
logger = logging.getLogger(__name__)


@router.get("/{jd_id}", response_model=JobDescriptionModel)
async def get_jd_endpoint(jd_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("get_jd_endpoint called for jd_id=%s", jd_id)
    jd = await get_jd(db, jd_id)
    if not jd:
        logger.warning("get_jd_endpoint job description not found for jd_id=%s", jd_id)
        raise HTTPException(status_code=404, detail="Job Description Not Found")
    logger.info("get_jd_endpoint succeeded for jd_id=%s", jd_id)
    return jd


@router.post("/", response_model=JobDescriptionModel)
async def create_jd_endpoint(
    jd_payload: JobDescriptionModel, db: AsyncSession = Depends(get_db)
):
    logger.info("create_jd_endpoint called for job_title=%s", jd_payload.job_title)
    response = await create_jd(db, jd_payload)
    logger.info("create_jd_endpoint succeeded for job_title=%s", jd_payload.job_title)
    return response


@router.delete("/{jd_id}")
async def delete_jd_endpoint(jd_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("delete_jd_endpoint called for jd_id=%s", jd_id)
    response = await delete_jd(db, jd_id)
    logger.info("delete_jd_endpoint succeeded for jd_id=%s", jd_id)
    return response
