from datetime import datetime

from pydantic import BaseModel, EmailStr

from tech_ziwei.models.user import SubscriptionTier


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    subscription_tier: SubscriptionTier
    created_at: datetime

    model_config = {"from_attributes": True}
