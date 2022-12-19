"""ユーザの認可と情報に関するビジネスロジックを提供するサービス層."""


import os
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_database
from models.token_model import TokenResponse
from models.user_model import UserEntity, UserResponse
from repositories.user_repository import get_credentials_by_username

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    """入力パスワードと保存されたパスワードが一致するかの検証関数."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db_session: Session, username: str, password: str) -> bool:
    """ユーザを認可できるかの検証関数."""
    user = get_credentials_by_username(db_session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return True


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    """アクセストークン作成関数."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserEntity:
    """アクセス中のユーザ情報を取得する関数."""
    db_session = next(get_database())
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_username = payload.get("sub")
        if token_username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_credentials_by_username(db_session, token_username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: UserEntity = Depends(get_current_user),
) -> UserResponse:
    """アクティブ状態のユーザ情報を取得する関数."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
    )


def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> TokenResponse:
    """認可とアクセストークン発行を行う関数."""
    db_session = next(get_database())
    user = authenticate_user(db_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )
