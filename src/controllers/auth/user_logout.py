from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import verify_token
from ...schemas.user import User as UserSchema


async def logout(db: AsyncSession, token: str):
    username = verify_token(token)  # raises 401 if invalid/expired

    stmt = select(UserSchema).where(UserSchema.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    return {"message": "Logged out successfully"}