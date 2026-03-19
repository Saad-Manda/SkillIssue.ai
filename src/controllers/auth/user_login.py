from .utils import get_user_for_login, verify_password, create_access_token
from ...models.user_model import LoginRequest, LoginResponse
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def login(db: AsyncSession, payload: LoginRequest):
    user = await get_user_for_login(db, payload.email, payload.username)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    user.is_active = True
    await db.commit()
    
    data = {
        'email': user.email,
        'sub': user.username,
        'role': ['user']
    }
    access_token = await create_access_token(data = data)
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id
    )
