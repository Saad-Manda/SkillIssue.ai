import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..controllers.user_profile.create_user_profile import create_user_profile
from ..controllers.user_profile.delete_user_profile import delete_user_profile
from ..controllers.user_profile.get_user_profile import get_user_profile
from ..controllers.user_profile.update_user_profile import update_user_profile
from ..database import get_db
from ..models.user_model import User as UserModel

router = APIRouter(prefix="/api/v1/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get("/{user_id}", response_model=UserModel)
async def get_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("get_user_endpoint called for user_id=%s", user_id)
    user = await get_user_profile(db, user_id)
    if not user:
        logger.warning("get_user_endpoint user not found for user_id=%s", user_id)
        raise HTTPException(status_code=404, detail="User Not Found")
    logger.info("get_user_endpoint succeeded for user_id=%s", user_id)
    return user


@router.post("/", response_model=UserModel)
async def create_user_endpoint(
    user_profile: UserModel, signup_token: str, db: AsyncSession = Depends(get_db)
):
    logger.info("create_user_endpoint called for username=%s", user_profile.username)
    response = await create_user_profile(db, user_profile, signup_token)
    logger.info("create_user_endpoint succeeded for username=%s", user_profile.username)
    return response


@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("delete_user_endpoint called for user_id=%s", user_id)
    response = await delete_user_profile(db, user_id)
    logger.info("delete_user_endpoint succeeded for user_id=%s", user_id)
    return response


@router.patch("/{user_id}")
async def update_user_endpoint(
    user_id: str, user_profile: dict, db: AsyncSession = Depends(get_db)
):
    logger.info("update_user_endpoint called for user_id=%s", user_id)
    response = await update_user_profile(db, user_id, user_profile)
    logger.info("update_user_endpoint succeeded for user_id=%s", user_id)
    return response
