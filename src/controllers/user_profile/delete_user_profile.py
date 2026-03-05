from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.education import Education as EducationSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.leadership import Leadership as LeadershipSchema

async def delete_user_profile(db: AsyncSession, user_id: str):
    # Fetch the existing user
    query = select(UserModel).where(UserModel.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.execute(delete(ExperienceSchema).where(ExperienceSchema.user_id == user_id))
    await db.execute(delete(EducationSchema).where(EducationSchema.user_id == user_id))
    await db.execute(delete(ProjectSchema).where(ProjectSchema.user_id == user_id))
    await db.execute(delete(LeadershipSchema).where(LeadershipSchema.user_id == user_id))
    await db.execute(delete(UserSchema).where(UserSchema.user_id == user_id))

    await db.commit()
    return True