import datetime
from datetime import timedelta

import jwt

from config import get_auth_data
from passlib.context import CryptContext

from fastapi import Request, HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['private_key'], algorithm=auth_data['algorithm'])


def get_token(request: Request):
    token = request.cookies.get('user_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token
