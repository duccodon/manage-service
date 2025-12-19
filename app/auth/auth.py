# auth.py
import jwt
from datetime import datetime, timedelta
from app.configs import config
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header

# from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Annotated

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"


class AuthUser(BaseModel):
    user_id: str
    role: str
    email: str


# Thiết lập OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_token_from_header(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    return authorization


async def get_current_user(token: Annotated[str, Depends(get_token_from_header)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = AuthUser(**payload)

    if user is None:
        raise credentials_exception
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str] | None = None):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[AuthUser, Depends(get_current_user)]):
        if self.allowed_roles is None:
            return user
        if user.role in self.allowed_roles:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permissions",
        )
