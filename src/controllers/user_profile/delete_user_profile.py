import logging

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user_model import User as UserModel
from ...schemas.education import Education as EducationSchema
from ...schemas.experience import Experience as ExperienceSchema
from ...schemas.leadership import Leadership as LeadershipSchema
from ...schemas.project import Project as ProjectSchema
from ...schemas.user import User as UserSchema

logger = logging.getLogger(__name__)


async def delete_user_profile(db: AsyncSession, user_id: str):
    logger.info("delete_user_profile controller called for user_id=%s", user_id)
    # Fetch the existing user
    query = select(UserSchema).where(UserSchema.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            "delete_user_profile controller not found for user_id=%s", user_id
        )
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(
        delete(ExperienceSchema).where(ExperienceSchema.user_id == user_id)
    )
    await db.execute(delete(EducationSchema).where(EducationSchema.user_id == user_id))
    await db.execute(delete(ProjectSchema).where(ProjectSchema.user_id == user_id))
    await db.execute(
        delete(LeadershipSchema).where(LeadershipSchema.user_id == user_id)
    )
    await db.execute(delete(UserSchema).where(UserSchema.user_id == user_id))

    await db.commit()
    logger.info("delete_user_profile controller succeeded for user_id=%s", user_id)
    return True
