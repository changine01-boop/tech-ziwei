from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tech_ziwei.database import get_db
from tech_ziwei.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from tech_ziwei.schemas.user import UserResponse
from tech_ziwei.services.auth import create_access_token, get_user_by_email, verify_password
from tech_ziwei.services.user import EmailAlreadyRegistered, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        user = await register_user(db, req)
    except EmailAlreadyRegistered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await get_user_by_email(db, req.email)
    if user is None or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")

    return TokenResponse(access_token=create_access_token(user.id))
