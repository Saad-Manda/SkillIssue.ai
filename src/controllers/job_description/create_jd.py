import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...schemas.jd import JobDescription as JobDescriptionSchema


async def create_jd(db: AsyncSession, jd_payload: dict):
    jd = JobDescriptionSchema(
        jd_id = str(uuid4()),
        job_title = jd_payload.get("job_title"),
        job_type = jd_payload.get("job_type", "full_time"),
        loc_type = jd_payload.get("loc_type", "remote"),
        location = jd_payload.get("location", ""),
        salary = jd_payload.get("salary", 0.0),
        min_experience = jd_payload.get("min_experience"),
        responsibilitites = jd_payload.get("responsibilitites", ""),
        required_qualification = jd_payload.get("required_qualification", ""),
        required_skills = jd_payload.get("required_skills", []),
        preferred_skills = jd_payload.get("preferred_skills", []),
        description = jd_payload.get("description", "")
    )
    db.add(jd)
    await db.commit()
    await db.refresh(jd)
    return jd