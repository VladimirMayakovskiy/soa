import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
from sqlalchemy.orm import Session
import jwt
import models
import db
import utils
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title='User Service API')


class UserSignupScheme(BaseModel):
    username: str # constr
    email: EmailStr
    password: constr(min_length=6)


class UserUpdateScheme(BaseModel):
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    birth_date: Optional[datetime.date] = Field(None)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")

    class Config:
        orm_mode = True


class UserResponseScheme(UserUpdateScheme):
    id: int
    username: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@app.post('/signup', response_model=UserResponseScheme)
def register(user_data: UserSignupScheme, db: Session = Depends(db.get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already register')

    hashed_password = utils.hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post('/login')
def login(user_data: UserSignupScheme, response: Response, db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not utils.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user credentials')
    access_token = utils.create_access_token({"sub": user.username})
    response.set_cookie("user_access_token", access_token, httponly=True)
    return {"access_token": access_token}


def get_current_user(token: str = Depends(utils.get_token), db: Session = Depends(db.get_db)):
    try:
        auth_data = utils.get_auth_data()
        payload = jwt.decode(token, auth_data['public_key'], algorithms=[auth_data['algorithm']])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    expire = payload.get('exp')
    if (not expire) or (datetime.datetime.fromtimestamp(expire, tz=datetime.timezone.utc) < datetime.datetime.now(datetime.timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is expired')

    username: str = payload.get('sub')
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


@app.put('/update', response_model=UserResponseScheme)
def update_profile(user_data: UserUpdateScheme, cur_user: models.User = Depends(get_current_user), db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.id == cur_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    user.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


@app.get('/profile', response_model=UserResponseScheme)
def get_user_profile(user: models.User = Depends(get_current_user)):
    return user


@app.get("/public_key")
async def get_public_key():
    auth_data = utils.get_auth_data()
    return {'public_key': auth_data['public_key'], 'algorithm': auth_data['algorithm']}


@app.delete("/clear")
async def clear(pattern: str, db: Session = Depends(db.get_db)):
    deleted_by_email = db.query(models.User).filter(models.User.email.like(f"%{pattern}%")).delete(synchronize_session=False)
    deleted_by_username = db.query(models.User).filter(models.User.username.like(f"%{pattern}%")).delete(synchronize_session=False)
    db.commit()

    return {
        "deleted_by_email": deleted_by_email,
        "deleted_by_username": deleted_by_username
    }

