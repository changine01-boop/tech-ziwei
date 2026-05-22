from fastapi import APIRouter, Depends

from tech_ziwei.models.user import User
from tech_ziwei.schemas.user import UserResponse
from .deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
