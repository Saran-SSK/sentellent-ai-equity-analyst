from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.investor_profile import InvestorProfile


class InvestorProfileRepository:
    """Database operations for investor profiles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_user(self, user_id: int) -> InvestorProfile | None:
        statement = select(InvestorProfile).where(InvestorProfile.user_id == user_id)
        return self.session.execute(statement).scalar_one_or_none()

    def create(self, profile_data: BaseModel | Mapping[str, Any]) -> InvestorProfile:
        if isinstance(profile_data, BaseModel):
            data = profile_data.model_dump(mode="json")
        else:
            data = dict(profile_data)

        db_profile = InvestorProfile(**data)
        self.session.add(db_profile)
        self.session.commit()
        self.session.refresh(db_profile)
        return db_profile

    def update(self, profile: InvestorProfile, updates: BaseModel | Mapping[str, Any]) -> InvestorProfile:
        update_data = self._to_update_data(updates)

        for field, value in update_data.items():
            setattr(profile, field, value)

        self.session.add(profile)
        self.session.commit()
        self.session.refresh(profile)
        return profile

    def upsert(self, user_id: int, profile_data: BaseModel | Mapping[str, Any]) -> InvestorProfile:
        existing = self.get_by_user(user_id)
        
        if existing:
            return self.update(existing, profile_data)
        else:
            if isinstance(profile_data, BaseModel):
                data = profile_data.model_dump(mode="json")
            else:
                data = dict(profile_data)
            
            data["user_id"] = user_id
            return self.create(data)

    @staticmethod
    def _to_update_data(updates: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(updates, BaseModel):
            data = updates.model_dump(exclude_unset=True, mode="json")
        else:
            data = dict(updates)

        writable_fields = {
            "risk_profile",
            "investment_horizon",
            "investment_style",
            "preferred_market",
            "preferred_sectors",
            "notes",
        }
        return {key: value for key, value in data.items() if key in writable_fields}
