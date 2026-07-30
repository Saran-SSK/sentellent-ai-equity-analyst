from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_watchlist_service
from app.api.v1.auth import get_current_user
from app.core.exceptions import (
    CompanyAlreadyInWatchlistError,
    CompanyNotFoundError,
    CompanyNotInWatchlistError,
    WatchlistNotFoundError,
)
from app.models.user import User
from app.schemas.watchlist import (
    WatchlistCompanyCreate,
    WatchlistCreate,
    WatchlistRead,
)
from app.services.watchlist import WatchlistService

router = APIRouter(
    prefix="/watchlists",
    tags=["watchlists"],
)


@router.post(
    "",
    response_model=WatchlistRead,
    status_code=status.HTTP_201_CREATED,
)
def create_watchlist(
    watchlist: WatchlistCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> WatchlistRead:
    return watchlist_service.create_watchlist(
        current_user.id,
        watchlist,
    )


@router.get(
    "",
    response_model=list[WatchlistRead],
)
def list_watchlists(
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[WatchlistRead]:
    return watchlist_service.list_watchlists(
        current_user.id,
        skip,
        limit,
    )


@router.get(
    "/{watchlist_id}",
    response_model=WatchlistRead,
)
def get_watchlist(
    watchlist_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> WatchlistRead:
    try:
        return watchlist_service.get_watchlist(
            current_user.id,
            watchlist_id,
        )
    except WatchlistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_watchlist(
    watchlist_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> Response:
    try:
        watchlist_service.delete_watchlist(
            current_user.id,
            watchlist_id,
        )
    except WatchlistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{watchlist_id}/companies",
    status_code=status.HTTP_201_CREATED,
)
def add_company(
    watchlist_id: int,
    request: WatchlistCompanyCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> dict[str, str]:
    try:
        watchlist_service.add_company(
            current_user.id,
            watchlist_id,
            request.company_id,
        )
    except WatchlistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyAlreadyInWatchlistError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return {"message": "Company added successfully."}


@router.delete(
    "/{watchlist_id}/companies/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_company(
    watchlist_id: int,
    company_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> Response:
    try:
        watchlist_service.remove_company(
            current_user.id,
            watchlist_id,
            company_id,
        )
    except WatchlistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CompanyNotInWatchlistError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
