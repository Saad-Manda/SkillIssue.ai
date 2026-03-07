import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...models.jd_model import JobDescription as JobDescriptionModel
from ...schemas.jd import JobDescription as JobDescriptionSchema

async def get_jd(db: AsyncSession, jd_id: str):
    try:
        stmt = select(JobDescriptionSchema).where(JobDescriptionSchema.jd_id == jd_id)
        result = await db.execute(statement=stmt)
        
        if not result:
            return None
        return JobDescriptionModel.model_validate(result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")