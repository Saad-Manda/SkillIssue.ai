import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...schemas.jd import JobDescription as JobDescriptionSchema


async def delete_jd(db: AsyncSession, jd_id: str):
    query = select(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
    result = await db.execute(query)
    jd = result.scalar_one_or_none()

    if jd is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.execute(delete(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id))

    await db.commit()
    return True