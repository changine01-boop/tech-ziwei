import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from tech_ziwei.database import get_db
from tech_ziwei.models.user import User
from tech_ziwei.services.payment import create_checkout_session, verify_webhook
from tech_ziwei.services.user import upgrade_to_basic
from .deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout-session")
async def checkout_session(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if current_user.subscription_tier != "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already unlocked",
        )
    url = create_checkout_session(current_user.id, current_user.email)
    return {"url": url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    user_id = verify_webhook(payload, sig)
    if user_id:
        await upgrade_to_basic(db, user_id)
        logger.info("Upgraded user %s via Stripe webhook", user_id)
    else:
        logger.debug("Stripe webhook event not actionable (no user_id resolved)")
    return {"received": True}
