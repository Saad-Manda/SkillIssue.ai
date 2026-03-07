import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from typing import Optional, List
from fastapi import HTTPException

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.education import Education as EducationSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.leadership import Leadership as LeadershipSchema

async def get_user_profile(db: AsyncSession, user_id: str):
    try:
        stmt = (
            select(UserSchema, ExperienceSchema, EducationSchema, ProjectSchema, LeadershipSchema)
            .outerjoin(ExperienceSchema, ExperienceSchema.user_id == UserSchema.user_id)
            .outerjoin(EducationSchema, EducationSchema.user_id == UserSchema.user_id)
            .outerjoin(ProjectSchema, ProjectSchema.user_id == UserSchema.user_id)
            .outerjoin(LeadershipSchema, LeadershipSchema.user_id == UserSchema.user_id)
            .where(UserSchema.user_id == user_id)
        )
        result = await db.execute(statement=stmt)
        
        if not result:
            return None
        return UserModel.model_validate(result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")