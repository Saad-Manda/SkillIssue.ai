from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ...models.user_model import SignupRequest, User
from .utils import create_access_token, hash_password, get_user_to_check

async def signup(db: AsyncSession, payload: SignupRequest):
    user = await get_user_to_check(db, payload.email, payload.username)
    
    if user:
        if user.email == payload.email and user.username == payload.username:
            raise HTTPException(status_code=400, detail="Username already in use")    #Login controller
        elif user.email == payload.email:
            raise HTTPException(status_code=400, detail="User with this email already exist")
        elif user.username == payload.username:
            raise HTTPException(status_code=400, detail="Username already in use")
            
    hashed_password = await hash_password(payload.password)
    
    user = User()
    user.user_id = str(uuid4())
    user.username = payload.username
    user.email = payload.email
    user.hashed_password = hashed_password
    
    data = {
        'email': user.email,
        'sub': user.username,
        'role': ['user']
    }
    token = await create_access_token(data)
    
    return {
        "token": token,
        "user": user
    }