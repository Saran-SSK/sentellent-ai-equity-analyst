from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository
from app.services.company import CompanyService
from app.services.user import UserService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_company_repository(db: Annotated[Session, Depends(get_db)]) -> CompanyRepository:
    return CompanyRepository(db)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)


def get_company_service(
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
) -> CompanyService:
    return CompanyService(company_repository)
