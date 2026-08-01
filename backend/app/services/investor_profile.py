from __future__ import annotations

from app.models.investor_profile import InvestorProfile
from app.repositories.investor_profile import InvestorProfileRepository
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileUpdate


class InvestorProfileService:
    """Business operations for investor profiles."""

    def __init__(
        self,
        investor_profile_repository: InvestorProfileRepository,
    ) -> None:
        self.investor_profile_repository = investor_profile_repository

    def get_profile(
        self,
        user_id: int,
    ) -> InvestorProfile | None:
        return self.investor_profile_repository.get_by_user(user_id)

    def upsert_profile(
        self,
        user_id: int,
        profile: InvestorProfileCreate | InvestorProfileUpdate,
    ) -> InvestorProfile:
        return self.investor_profile_repository.upsert(user_id, profile)
