from typing import Annotated
from fastapi import HTTPException, status, Depends
from app.core.security import oauth2_scheme, decode_token
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        data = decode_token(token)
        uid = int(data.get("sub", "0"))
    except (ValueError, JWTError, ExpiredSignatureError, HTTPException):
        raise credentials_exception
    user = db.get(User, uid)
    if not user:
        raise credentials_exception
    return user
    
def get_current_user_id(
    user: Annotated[User, Depends(get_current_user)]
) -> int:
    return user.id

def get_current_user_username(
    user: Annotated[User, Depends(get_current_user)]
) -> str:
    return user.username