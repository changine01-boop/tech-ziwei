"""Shared FastAPI dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from tech_ziwei.database import get_db
from tech_ziwei.models.user import User
from tech_ziwei.services.auth import decode_token, get_user_by_id

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(credentials.credentials)
    except JWTError:
        raise unauthorized

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user
