"""User creation and retrieval."""

from sqlalchemy.ext.asyncio import AsyncSession

from tech_ziwei.models.user import User
from tech_ziwei.schemas.auth import RegisterRequest
from .auth import hash_password, get_user_by_email


class EmailAlreadyRegistered(Exception):
    pass


async def register_user(db: AsyncSession, req: RegisterRequest) -> User:
    if await get_user_by_email(db, req.email):
        raise EmailAlreadyRegistered(req.email)

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
