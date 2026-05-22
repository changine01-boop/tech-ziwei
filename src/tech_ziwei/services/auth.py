"""JWT token creation and password hashing."""

from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tech_ziwei.config import settings
from tech_ziwei.models.user import User

_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_token(token: str) -> str:
    """Return the subject (user id) from a valid token, or raise JWTError."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    sub: str | None = payload.get("sub")
    if sub is None:
        raise JWTError("Missing subject")
    return sub


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
