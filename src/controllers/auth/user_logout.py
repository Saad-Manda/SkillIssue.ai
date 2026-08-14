import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.user import User as UserSchema
from .utils import verify_token

logger = logging.getLogger(__name__)


async def logout(db: AsyncSession, token: str):
    logger.info("logout controller called")
    username = verify_token(token)  # raises 401 if invalid/expired

    stmt = select(UserSchema).where(UserSchema.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("logout controller user not found for username=%s", username)
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    response = {"message": "Logged out successfully"}
    logger.info("logout controller succeeded for username=%s", username)
    return response
