from fastapi import HTTPException
from .utils import get_user_profile, create_access_token, verify_pswd
from sqlalchemy.ext.asyncio import AsyncSession






def login(db: AsyncSession, username: str):
    user_dict = get_user_profile(db, username)
    if not user_dict:
        raise HTTPException(status_code=400, detail='Invalid Username')
    if not verify_pswd(user_dict.password, user_dict['hashed_pswd']):
        raise HTTPException(status_code=400, detail='Invalid Password')
    
    access_token = create_access_token(data = { 'sub': user_dict.username})
    return {'access_token': access_token, 'token_type': 'bearer'}
