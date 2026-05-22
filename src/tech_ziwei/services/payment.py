"""Stripe payment integration."""

import stripe
from fastapi import HTTPException
from tech_ziwei.config import settings

_PRICE_CENTS = 999  # $9.99


def create_checkout_session(user_id: str, user_email: str) -> str:
    """Create a Stripe Checkout Session and return the hosted URL."""
    try:
        session = stripe.checkout.Session.create(
            api_key=settings.stripe_secret_key,
            mode="payment",
            customer_email=user_email,
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": _PRICE_CENTS,
                        "product_data": {
                            "name": "Tech Zi Wei — Full Report Access",
                            "description": (
                                "Unlock complete AI-powered psychological readings "
                                "for all your Zi Wei Dou Shu charts."
                            ),
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata={"user_id": user_id},
            success_url=(
                f"{settings.frontend_url}/payment/success"
                "?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=f"{settings.frontend_url}/payment/cancel",
        )
        return session.url or ""
    except stripe.error.StripeError as e:
        user_message = getattr(e, "user_message", None) or str(e)
        raise HTTPException(
            status_code=502,
            detail=f"Payment provider error: {user_message}",
        )


def verify_webhook(payload: bytes, sig_header: str) -> str | None:
    """
    Validate a Stripe webhook and return user_id on successful payment.
    Returns None if the event is irrelevant or verification fails.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return None

    if event["type"] != "checkout.session.completed":
        return None

    session = event["data"]["object"]
    if session.get("payment_status") != "paid":
        return None

    return session.get("metadata", {}).get("user_id")
