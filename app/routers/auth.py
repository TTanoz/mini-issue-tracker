from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import TokenResponse, LoginIn
from app.core.security import verify_pw, hash_pw, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Username already registered")

    user = User(
        username=payload.username,
        password_hash=hash_pw(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(
    form: LoginIn,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_pw(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")


    token = create_token(user_id=user.id)
    return TokenResponse(access_token=token)