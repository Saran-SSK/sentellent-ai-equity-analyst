from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate


class CompanyRepository:
    """Database operations for companies."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: int) -> Company | None:
        statement = select(Company).where(Company.id == id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_symbol(self, symbol: str) -> Company | None:
        normalized_symbol = symbol.strip().upper()
        statement = select(Company).where(Company.symbol == normalized_symbol)
        return self.session.execute(statement).scalar_one_or_none()

    def list_companies(self, skip: int = 0, limit: int = 100) -> list[Company]:
        statement = select(Company).offset(skip).limit(limit)
        return list(self.session.execute(statement).scalars().all())

    def create(self, company: CompanyCreate) -> Company:
        db_company = Company(**company.model_dump(mode="json"))
        self.session.add(db_company)
        self.session.commit()
        self.session.refresh(db_company)
        return db_company

    def update(self, company: Company, updates: BaseModel | Mapping[str, Any]) -> Company:
        update_data = self._to_update_data(updates)

        for field, value in update_data.items():
            setattr(company, field, value)

        self.session.add(company)
        self.session.commit()
        self.session.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.session.delete(company)
        self.session.commit()

    @staticmethod
    def _to_update_data(updates: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(updates, BaseModel):
            data = updates.model_dump(exclude_unset=True, mode="json")
        else:
            data = dict(updates)

        writable_fields = {
            "symbol",
            "name",
            "exchange",
            "sector",
            "industry",
            "country",
            "currency",
            "description",
            "website",
            "is_active",
        }
        return {key: value for key, value in data.items() if key in writable_fields}
