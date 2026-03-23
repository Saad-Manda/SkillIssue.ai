import logging
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.user_model import SignupRequest, SignupResponse
from .utils import (
    create_access_token,
    create_signup_token,
    get_user_to_check,
    hash_password,
)

logger = logging.getLogger(__name__)


async def signup(db: AsyncSession, payload: SignupRequest):
    logger.info(
        "signup controller called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    user = await get_user_to_check(db, payload.email, payload.username)

    if user:
        logger.warning(
            "signup controller found existing user conflict for email=%s username=%s",
            payload.email,
            payload.username,
        )
        if user.email == payload.email and user.username == payload.username:
            raise HTTPException(
                status_code=409, detail="User already exists"
            )  # Login controller
        elif user.email == payload.email:
            raise HTTPException(status_code=409, detail="Email already in use")
        elif user.username == payload.username:
            raise HTTPException(status_code=409, detail="Username already in use")

    hashed_password = await hash_password(payload.password)

    access_data = {"email": payload.email, "sub": payload.username, "role": ["user"]}
    access_token = await create_access_token(access_data)

    signup_data = {
        "email": payload.email,
        "hashed_password": hashed_password,
        "sub": payload.username,
        "role": ["user"],
    }
    signup_token = await create_signup_token(signup_data)

    response = SignupResponse(
        access_token=access_token,
        signup_token=signup_token,
    )
    logger.info(
        "signup controller succeeded for email=%s username=%s",
        payload.email,
        payload.username,
    )
    return response
