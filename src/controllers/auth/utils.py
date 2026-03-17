from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from sqlalchemy.orm import selectinload

from ...models.user_model import User as UserModel
from ...schemas.user import User as UserSchema

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from authlib.jose import JoseError, jwt
from fastapi import HTTPException
from ...config import settings

pswd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_access_token(data: dict):
    header = {'alg': settings.ALGORITHM}
    expire = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRY_MINUTES)
    payload = data.copy()
    payload.update({'exp': expire})
    return jwt.encode(header, payload, settings.SECRET_KEY).decode('utf-8')

def verify_token(token: str):
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
        claims.validate()
        username = claims.get('sub')
        if username is None:
            raise HTTPException(status_code=402, detail='Token Missing')
        return username
    except JoseError:
        raise HTTPException(status_code=401, detail="Couldn't validate credentials")

def verify_pswd(plain_pswd, hashed_pswd):
    return pswd_context.verify(plain_pswd, hashed_pswd)

async def get_user_profile(db: AsyncSession, username: str):
    stmt = (
        select(UserSchema)
        .where(UserSchema.username == username)
    )
    result = await db.execute(statement=stmt)
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        return None
    return user_obj