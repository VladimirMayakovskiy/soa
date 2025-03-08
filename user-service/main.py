import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models, db, utils


app = FastAPI(title='User Service API')


class UserRegister(BaseModel):
    username: str # constr
    email: EmailStr
    password: constr(min_length=6)


class UserProfile(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[datetime.date]
    email: Optional[EmailStr]
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")

    class Config:
        orm_mode = True


class UserResponse(UserProfile):
    id: int
    username: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@app.post('/signup', response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(db.get_db)):
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
def login(user_data: UserRegister, response: Response, db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not utils.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user credentials')
    access_token = utils.create_access_token({"sub": user.username})
    response.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=True
    )
    return {"access_token": access_token}


def get_current_user(token: str = Depends(utils.get_token), db: Session = Depends(db.get_db)):
    try:
        auth_data = utils.get_auth_data()
        payload = jwt.decode(token, auth_data['public_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
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


@app.put('/update', response_model=UserProfile)
def update_profile(user_data: UserProfile, cur_user: models.User = Depends(get_current_user), db: Session = Depends(db.get_db)):
    user = db.query(models.User).filter(models.User.id == cur_user.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    user.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


@app.get('/profile', response_model=UserProfile)
def get_user_profile(user: models.User = Depends(get_current_user)):
    return user
