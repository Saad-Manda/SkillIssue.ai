from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.user_model import SignupResponse, SignupRequest, LoginResponse, LoginRequest
from ..controllers.auth.user_signup import signup
from ..controllers.auth.user_login import login

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
async def signup_endpoint(payload: SignupRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await signup(db, payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/login", response_model=LoginResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await login(db, payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
