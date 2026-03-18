from .utils import verify_password, get_user_to_check, create_access_token
from ...models.user_model import LoginRequest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def login(db: AsyncSession, payload: LoginRequest):
    user = await get_user_to_check(db, payload.email, payload.username)
    if not user:
        raise HTTPException(status_code=400, detail='Invalid Email')
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Invalid Credentials')
    
    data = {
        'email': user.email,
        'sub': user.username,
        'role': ['user']
    }
    access_token = await create_access_token(data = data)
    return {'access_token': access_token, 'token_type': 'bearer'}