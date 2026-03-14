import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...schemas.jd import JobDescription as JobDescriptionSchema
from ...models.jd_model import JobDescription as JobDescriptionModel


async def create_jd(db: AsyncSession, jd_payload: JobDescriptionModel):
    jd = JobDescriptionSchema(
        jd_id = str(uuid4()),
        job_title = jd_payload.job_title,
        job_type = jd_payload.job_type,
        loc_type = jd_payload.loc_type,
        location = jd_payload.location,
        salary = jd_payload.salary or 0.0,
        min_experience = jd_payload.min_experience,
        responsibilities = jd_payload.responsibilities,
        required_qualification = jd_payload.required_qualification,
        required_skills = jd_payload.required_skills,
        preferred_skills = jd_payload.preferred_skills,
        description = jd_payload.description
    )
    db.add(jd)
    await db.commit()
    await db.refresh(jd)
    return jd