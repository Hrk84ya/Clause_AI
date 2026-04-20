import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from src.database import get_db
from src.dependencies import get_current_user
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    # Create refresh token
    raw_token, hashed_token = create_refresh_token()
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hashed_token,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(refresh_token_record)
    await db.flush()

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
    )

    return RegisterResponse(
        id=user.id,
        email=user.email,
        access_token=access_token,
        refresh_token=raw_token,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return access/refresh tokens."""
    # Look up user by email
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create refresh token
    raw_token, hashed_token = create_refresh_token()
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hashed_token,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(refresh_token_record)
    await db.flush()

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange a valid refresh token for a new access token."""
    # Hash the provided refresh token
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()

    # Look up the hash in the database
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token_record = result.scalar_one_or_none()

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Check if expired
    if token_record.expires_at < datetime.now(timezone.utc):
        # Clean up expired token
        await db.delete(token_record)
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # Create new access token using the user_id from the token record
    access_token = create_access_token(
        data={"sub": str(token_record.user_id)},
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=body.refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(
    body: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Logout by invalidating the refresh token."""
    # Hash the provided refresh token
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()

    # Delete matching record from refresh_tokens table
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token_record = result.scalar_one_or_none()
    if token_record is not None:
        await db.delete(token_record)
        await db.flush()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the current authenticated user's profile."""
    return UserResponse.model_validate(current_user)
