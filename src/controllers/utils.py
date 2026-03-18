from authlib.jose import JoseError, jwt
from fastapi import HTTPException
from ..config import settings

def verify_access_token(token: str):
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
        claims.validate()
        username = claims.get('sub')
        if username is None:
            raise HTTPException(status_code=402, detail='Token Missing')
        return username
    except JoseError:
        raise HTTPException(status_code=401, detail="Couldn't validate credentials")


def verify_signup_token(token: str):
    try:
        claims = jwt.decode(token, settings.SECRET_KEY)
        claims.validate()
        if claims.get('sub') is None:
            raise HTTPException(status_code=402, detail='Token Missing')
        return claims
    except JoseError:
        raise HTTPException(status_code=401, detail="Couldn't validate credentials")