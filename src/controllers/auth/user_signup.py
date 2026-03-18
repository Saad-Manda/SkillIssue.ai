from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...models.user_model import SignupRequest, SignupResponse
from .utils import create_access_token, create_signup_token, hash_password, get_user_to_check

async def signup(db: AsyncSession, payload: SignupRequest):
    user = await get_user_to_check(db, payload.email, payload.username)
    
    if user:
        if user.email == payload.email and user.username == payload.username:
            raise HTTPException(status_code=400, detail="User already exist")    #Login controller
        elif user.email == payload.email:
            raise HTTPException(status_code=400, detail="User with this email already exist")
        elif user.username == payload.username:
            raise HTTPException(status_code=400, detail="Username already in use")
    else:
        raise HTTPException(status_code=400, detail="Missing Credentials")
            
    hashed_password = await hash_password(payload.password)
    
    access_data = {
        'email': user.email,
        'sub': user.username,
        'role': ['user']
    }
    access_token = await create_access_token(access_data)

    signup_data = {
        'email': user.email,
        'hashed_password': hashed_password,
        'sub': user.username,
        'role': ['user']
    }
    signup_token = await create_signup_token(signup_data)
    
    return SignupResponse(
        access_token=access_token,
        signup_token=signup_token,
    )