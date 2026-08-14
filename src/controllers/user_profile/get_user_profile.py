import logging

from sqlalchemy import delete, join, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema

logger = logging.getLogger(__name__)


async def get_user_profile(db: AsyncSession, user_id: str):
    logger.info("get_user_profile controller called for user_id=%s", user_id)
    stmt = (
        select(UserSchema)
        .options(
            selectinload(UserSchema.experiences),
            selectinload(UserSchema.educations),
            selectinload(UserSchema.projects),
            selectinload(UserSchema.leaderships),
        )
        .where(UserSchema.user_id == user_id)
    )
    result = await db.execute(statement=stmt)
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        logger.warning("get_user_profile controller not found for user_id=%s", user_id)
        return None

    response = UserModel.model_validate(user_obj)
    logger.info("get_user_profile controller succeeded for user_id=%s", user_id)
    return response
