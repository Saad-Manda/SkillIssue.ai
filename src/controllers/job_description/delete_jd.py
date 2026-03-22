import logging
import os
from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import delete, join, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.jd import JobDescription as JobDescriptionSchema

logger = logging.getLogger(__name__)


async def delete_jd(db: AsyncSession, jd_id: str):
    logger.info("delete_jd controller called for jd_id=%s", jd_id)
    query = select(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
    result = await db.execute(query)
    jd = result.scalar_one_or_none()

    if jd is None:
        logger.warning("delete_jd controller not found for jd_id=%s", jd_id)
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(
        delete(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
    )

    await db.commit()
    logger.info("delete_jd controller succeeded for jd_id=%s", jd_id)
    return True
