import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers.auth.user_login import login
from ..controllers.auth.user_logout import logout
from ..controllers.auth.user_signup import signup
from ..database import get_db
from ..models.user_model import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=SignupResponse)
async def signup_endpoint(payload: SignupRequest, db: AsyncSession = Depends(get_db)):
    logger.info(
        "signup_endpoint called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    try:
        response = await signup(db, payload)
        logger.info(
            "signup_endpoint succeeded for email=%s username=%s",
            payload.email,
            payload.username,
        )
        return response
    except Exception as e:
        logger.exception(
            "signup_endpoint failed for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info(
        "login_endpoint called for email=%s username=%s",
        payload.email,
        payload.username,
    )
    try:
        response = await login(db, payload)
        logger.info(
            "login_endpoint succeeded for email=%s username=%s",
            payload.email,
            payload.username,
        )
        return response
    except Exception as e:
        logger.exception(
            "login_endpoint failed for email=%s username=%s",
            payload.email,
            payload.username,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/logout")
async def logout_endpoint(
    authorization: str,
    db: AsyncSession = Depends(get_db),
):
    logger.info("logout_endpoint called")
    try:
        logger.debug(
            "logout_endpoint authorization header present=%s", bool(authorization)
        )
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("logout_endpoint invalid authorization header")
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization.split(" ", 1)[1].strip()
        response = await logout(db, token)
        logger.info("logout_endpoint succeeded")
        return response

    except HTTPException:
        logger.warning("logout_endpoint raised HTTPException")
        raise
    except Exception as e:
        logger.exception("logout_endpoint failed unexpectedly")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
