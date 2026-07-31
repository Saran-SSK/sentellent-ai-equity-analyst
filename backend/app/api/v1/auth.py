from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import get_user_service
from app.core import security
from app.core.google_oauth import GoogleOAuthError, get_google_user_info
from app.core.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, LoginRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    try:
        return user_service.create_user(user)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=Token)
def login_user(
    credentials: LoginRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Token:
    user = user_service.authenticate_user(
        email=str(credentials.email),
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@router.post("/google", response_model=Token)
def google_auth(
    request: GoogleAuthRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> Token:
    """Authenticate with Google OAuth ID token."""
    try:
        # Verify the Google ID token and extract user info
        google_user_info = get_google_user_info(request.id_token)
        
        # Create or get the user
        user = user_service.get_or_create_google_user(
            google_id=google_user_info["google_id"],
            email=google_user_info["email"],
            full_name=google_user_info["full_name"],
            google_avatar_url=google_user_info["google_avatar_url"],
        )
        
        # Create JWT token
        access_token = security.create_access_token(subject=str(user.id))
        return Token(access_token=access_token)
        
    except GoogleOAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    subject = payload.get("sub")
    if subject is None:
        raise credentials_exception

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise credentials_exception from exc

    try:
        return user_service.get_user(user_id)
    except UserNotFoundError as exc:
        raise credentials_exception from exc
