from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.deps import get_current_user
from app.core.security import verify_pw, hash_pw

router = APIRouter(prefix="/users", tags=["users"])

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@router.get("/me", response_model=UserRead)
def get_me(current: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return current

@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    db: Annotated[Session, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> None:
    if not verify_pw(payload.old_password, current.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current.password_hash = hash_pw(payload.new_password)
    db.add(current)
    db.commit()
    return

@router.get("/", response_model=list[UserRead], dependencies=[Depends(get_current_user)])
def list_users(db: Annotated[Session, Depends(get_db)],
               skip: int = Query(0, ge=0),
               limit: int = Query(50, ge=1, le=200),
               q: str | None = Query(None, description="Filter by username (icontains)"),
               sort_by: Literal["id", "username", "created_at"] = "id",
               sort_dir: Literal["asc", "desc"] = "asc") -> list[UserRead]:
    query = db.query(User)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    col = getattr(User, sort_by)
    order = asc(col) if sort_dir == "asc" else desc(col)
    query = query.order_by(order)
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_user)])
def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user