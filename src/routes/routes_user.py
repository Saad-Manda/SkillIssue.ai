from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db

from ..models.user_model import User as UserModel
from ..controllers.user_profile.create_user_profile import create_user_profile
from ..controllers.user_profile.get_user_profile import get_user_profile
from ..controllers.user_profile.update_user_profile import update_user_profile
from ..controllers.user_profile.delete_user_profile import delete_user_profile

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/{user_id}", response_model=UserModel)
async def get_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user

@router.post("/", response_model=UserModel)
async def create_user_endpoint(user_profile: dict, db: AsyncSession = Depends(get_db)):
    return await create_user_profile(db, user_profile)

@router.delete("/{user_id}")
async def delete_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    return await delete_user_profile(user_id, db)

@router.patch("/{user_id}")
async def update_user_endpoint(user_id: str, user_profile: dict, db: AsyncSession = Depends(get_db)):
    return await update_user_profile(db, user_id, user_profile)