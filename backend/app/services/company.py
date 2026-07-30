from __future__ import annotations

from app.core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Business operations for companies."""

    def __init__(self, company_repository: CompanyRepository) -> None:
        self.company_repository = company_repository

    def create_company(self, company: CompanyCreate) -> Company:
        existing_company = self.company_repository.get_by_symbol(company.symbol)
        if existing_company is not None:
            raise CompanyAlreadyExistsError(company.symbol)

        return self.company_repository.create(company)

    def get_company(self, id: int) -> Company:
        company = self.company_repository.get_by_id(id)
        if company is None:
            raise CompanyNotFoundError(id)

        return company

    def get_company_by_symbol(self, symbol: str) -> Company | None:
        return self.company_repository.get_by_symbol(symbol.upper())

    def list_companies(self, skip: int = 0, limit: int = 100) -> list[Company]:
        return self.company_repository.list_companies(skip=skip, limit=limit)

    def update_company(self, id: int, updates: CompanyUpdate) -> Company:
        company = self.get_company(id)
        update_data = updates.model_dump(exclude_unset=True, mode="json")

        symbol = update_data.get("symbol")
        if symbol is not None and symbol != company.symbol:
            existing_company = self.company_repository.get_by_symbol(symbol)
            if existing_company is not None:
                raise CompanyAlreadyExistsError(symbol)

        return self.company_repository.update(company=company, updates=update_data)

    def delete_company(self, id: int) -> None:
        company = self.get_company(id)
        self.company_repository.delete(company)
