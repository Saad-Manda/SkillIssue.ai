import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user_model import LoginRequest, LoginResponse
from .utils import create_access_token, get_user_for_login, verify_password

logger = logging.getLogger(__name__)


async def login(db: AsyncSession, payload: LoginRequest):
    logger.info(
        "login controller called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    user = await get_user_for_login(db, payload.email, payload.username)
    if not user:
        logger.warning(
            "login controller invalid credentials: user not found for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        logger.warning(
            "login controller invalid credentials: password mismatch for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.is_active = True
    await db.commit()

    data = {"email": user.email, "sub": user.username, "role": ["user"]}
    access_token = await create_access_token(data=data)
    response = LoginResponse(
        access_token=access_token, token_type="bearer", user_id=user.user_id
    )
    logger.info("login controller succeeded for user_id=%s", user.user_id)
    return response
