from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_investor_profile_service
from app.api.v1.auth import get_current_user
from app.models.investor_profile import InvestorProfile
from app.models.user import User
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileRead, InvestorProfileUpdate
from app.services.investor_profile import InvestorProfileService

router = APIRouter(
    prefix="/investor-profile",
    tags=["investor-profile"],
)


@router.get(
    "",
    response_model=InvestorProfileRead,
)
def get_investor_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    investor_profile_service: Annotated[
        InvestorProfileService,
        Depends(get_investor_profile_service),
    ],
) -> InvestorProfile:
    profile = investor_profile_service.get_profile(current_user.id)
    
    if profile is None:
        # Create an empty profile for the user
        empty_profile = InvestorProfileCreate()
        profile = investor_profile_service.upsert_profile(
            current_user.id,
            empty_profile,
        )
    
    return profile


@router.put(
    "",
    response_model=InvestorProfileRead,
)
def update_investor_profile(
    profile_update: InvestorProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    investor_profile_service: Annotated[
        InvestorProfileService,
        Depends(get_investor_profile_service),
    ],
) -> InvestorProfile:
    return investor_profile_service.upsert_profile(
        current_user.id,
        profile_update,
    )
