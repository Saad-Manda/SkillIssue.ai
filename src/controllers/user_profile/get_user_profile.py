from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from sqlalchemy.orm import selectinload

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema

async def get_user_profile(db: AsyncSession, user_id: str):
    stmt = (
        select(UserSchema)
        .options(
            selectinload(UserSchema.experiences),
            selectinload(UserSchema.educations),
            selectinload(UserSchema.projects),
            selectinload(UserSchema.leaderships)
        )
        .where(UserSchema.user_id == user_id)
    )
    result = await db.execute(statement=stmt)
    user_obj = result.scalar_one_or_none()
    
    if not user_obj:
        return None
    
    return UserModel.model_validate(user_obj)