from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_company_service
from app.api.v1.auth import get_current_user
from app.core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(
    company: CompanyCreate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    """Create a new company record."""
    try:
        return company_service.create_company(company)
    except CompanyAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[CompanyRead])
def list_companies(
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[CompanyRead]:
    """List all companies with pagination."""
    return company_service.list_companies(skip=skip, limit=limit)


@router.get("/search")
def search_companies(
    q: Annotated[
        str, Query(..., description="Search query for company name or symbol")
    ],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> list[dict[str, object]]:
    """Search for companies using market data provider."""
    return company_service.search_companies(q)


@router.get("/recommendations")
def get_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    limit: Annotated[int, Query(ge=1, le=12)] = 6,
) -> list[dict[str, object]]:
    """Return personalized company recommendations for the current user."""
    return company_service.get_recommendations(current_user.id, limit=limit)


@router.get("/recently-viewed")
def get_recently_viewed(
    current_user: Annotated[User, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
) -> list[dict[str, object]]:
    """Return recently viewed companies for the current user."""
    return company_service.get_recently_viewed(current_user.id, limit=limit)


@router.post("/{symbol}/viewed")
def track_company_view(
    symbol: str,
    current_user: Annotated[User, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> dict[str, str]:
    """Record that the current user viewed a company detail page."""
    print(f"Tracking company view: user_id={current_user.id}, symbol={symbol}")
    company_service.track_recent_view(current_user.id, symbol)
    print(f"Company view tracked successfully")
    return {"message": "Company view recorded."}


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    """Retrieve a company by its database ID."""
    try:
        return company_service.get_company(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: int,
    updates: CompanyUpdate,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyRead:
    """Update a company by its database ID."""
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
    """Delete a company by its database ID."""
    try:
        company_service.delete_company(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{symbol}/profile")
def get_company_profile(
    symbol: str,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> dict[str, object]:
    """Fetch company profile from market data provider."""
    profile = company_service.fetch_company(symbol)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with symbol '{symbol}' not found in market data",
        )

    return profile


@router.get("/{symbol}/quote")
def get_company_quote(
    symbol: str,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> dict[str, object]:
    """Fetch latest market quote."""
    quote = company_service.fetch_quote(symbol)

    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote for symbol '{symbol}' not found in market data",
        )

    return quote


@router.get("/{symbol}/financials")
def get_company_financials(
    symbol: str,
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> dict[str, object]:
    """Fetch latest reported financial statements."""
    financials = company_service.get_financials(symbol)

    if not financials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Financial statements for '{symbol}' not found.",
        )

    return financials


@router.get("/{symbol}/news")
def get_company_news(
    symbol: str,
    from_date: Annotated[
        str,
        Query(description="Start date in YYYY-MM-DD format"),
    ],
    to_date: Annotated[
        str,
        Query(description="End date in YYYY-MM-DD format"),
    ],
    company_service: Annotated[
        CompanyService,
        Depends(get_company_service),
    ],
) -> list[dict[str, object]]:
    """Fetch company news from the market data provider."""
    # First check if company exists
    profile = company_service.fetch_company(symbol)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with symbol '{symbol}' not found.",
        )

    # Fetch news (may be empty list)
    news = company_service.get_company_news(
        symbol,
        from_date,
        to_date,
    )

    # Return empty list with 200 OK if no news available
    return news if news else []


@router.get("/{symbol}/history")
def get_historical_prices(
    symbol: str,
    resolution: Annotated[
        str,
        Query(description="Resolution (1,5,15,30,60,D,W,M)"),
    ],
    from_timestamp: Annotated[
        int,
        Query(description="Unix start timestamp"),
    ],
    to_timestamp: Annotated[
        int,
        Query(description="Unix end timestamp"),
    ],
    company_service: Annotated[
        CompanyService,
        Depends(get_company_service),
    ],
) -> dict[str, object]:
    """Fetch historical OHLCV price data."""
    history = company_service.get_historical_prices(
        symbol,
        resolution,
        from_timestamp,
        to_timestamp,
    )

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{symbol}'.",
        )

    return history
