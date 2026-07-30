from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_holding_service, get_portfolio_service
from app.api.v1.auth import get_current_user
from app.core.exceptions import (
    CompanyNotFoundError,
    HoldingAlreadyExistsError,
    HoldingNotFoundError,
    PortfolioNotFoundError,
)
from app.models.user import User
from app.schemas.holding import HoldingCreate, HoldingUpdate
from app.schemas.portfolio import PortfolioCreate, PortfolioRead, PortfolioUpdate
from app.services.holding import HoldingService
from app.services.portfolio import PortfolioService

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolios"],
)


@router.post(
    "",
    response_model=PortfolioRead,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
) -> PortfolioRead:
    return portfolio_service.create_portfolio(
        current_user.id,
        portfolio,
    )


@router.get(
    "",
    response_model=list[PortfolioRead],
)
def list_portfolios(
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[PortfolioRead]:
    return portfolio_service.list_portfolios(
        current_user.id,
        skip,
        limit,
    )


@router.get(
    "/{portfolio_id}",
    response_model=PortfolioRead,
)
def get_portfolio(
    portfolio_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
) -> PortfolioRead:
    try:
        return portfolio_service.get_portfolio(
            current_user.id,
            portfolio_id,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{portfolio_id}",
    response_model=PortfolioRead,
)
def update_portfolio(
    portfolio_id: int,
    updates: PortfolioUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
) -> PortfolioRead:
    try:
        return portfolio_service.update_portfolio(
            current_user.id,
            portfolio_id,
            updates,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_portfolio(
    portfolio_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
) -> Response:
    try:
        portfolio_service.delete_portfolio(
            current_user.id,
            portfolio_id,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{portfolio_id}/holdings",
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    portfolio_id: int,
    holding: HoldingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    holding_service: Annotated[
        HoldingService,
        Depends(get_holding_service),
    ],
) -> dict[str, str]:
    try:
        holding_service.create_holding(
            current_user.id,
            portfolio_id,
            holding,
        )
    except PortfolioNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except HoldingAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return {"message": "Holding created successfully."}


@router.patch(
    "/holdings/{holding_id}",
    status_code=status.HTTP_200_OK,
)
def update_holding(
    holding_id: int,
    updates: HoldingUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    holding_service: Annotated[
        HoldingService,
        Depends(get_holding_service),
    ],
) -> dict[str, str]:
    try:
        holding_service.update_holding(
            holding_id,
            updates,
        )
    except HoldingNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {"message": "Holding updated successfully."}


@router.delete(
    "/holdings/{holding_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holding(
    holding_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    holding_service: Annotated[
        HoldingService,
        Depends(get_holding_service),
    ],
) -> Response:
    try:
        holding_service.delete_holding(
            holding_id,
        )
    except HoldingNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
