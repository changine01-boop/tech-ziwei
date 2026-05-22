"""User creation and retrieval."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tech_ziwei.models.user import User, SubscriptionTier
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


async def upgrade_to_basic(
    db: AsyncSession, user_id: str, stripe_customer_id: str | None = None
) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    user.subscription_tier = SubscriptionTier.BASIC
    if stripe_customer_id:
        user.stripe_customer_id = stripe_customer_id
    await db.commit()
    await db.refresh(user)
    return user
