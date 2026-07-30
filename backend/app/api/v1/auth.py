from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_user_service
from app.core import security
from app.core.exceptions import UserAlreadyExistsError
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


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
