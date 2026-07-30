from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_company_service
from app.core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(
    company: CompanyCreate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    try:
        return company_service.create_company(company)
    except CompanyAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    try:
        return company_service.get_company(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[CompanyRead])
def list_companies(
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[CompanyRead]:
    return company_service.list_companies(skip=skip, limit=limit)


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: int,
    updates: CompanyUpdate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    try:
        return company_service.update_company(company_id, updates)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> Response:
    try:
        company_service.delete_company(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
