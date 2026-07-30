from __future__ import annotations

from app.core.exceptions import (
    CompanyAlreadyInWatchlistError,
    CompanyNotInWatchlistError,
    CompanyNotFoundError,
    WatchlistNotFoundError,
)
from app.models.watchlist import Watchlist
from app.repositories.company import CompanyRepository
from app.repositories.watchlist import WatchlistRepository
from app.schemas.watchlist import WatchlistCreate


class WatchlistService:
    """Business operations for watchlists."""

    def __init__(
        self,
        watchlist_repository: WatchlistRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self.watchlist_repository = watchlist_repository
        self.company_repository = company_repository

    def create_watchlist(
        self,
        user_id: int,
        watchlist: WatchlistCreate,
    ) -> Watchlist:
        return self.watchlist_repository.create(user_id, watchlist)

    def get_watchlist(
        self,
        user_id: int,
        watchlist_id: int,
    ) -> Watchlist:
        watchlist = self.watchlist_repository.get_by_id_for_user(
            watchlist_id,
            user_id,
        )

        if watchlist is None:
            raise WatchlistNotFoundError(watchlist_id)

        return watchlist

    def list_watchlists(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Watchlist]:
        return self.watchlist_repository.list_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def delete_watchlist(
        self,
        user_id: int,
        watchlist_id: int,
    ) -> None:
        watchlist = self.get_watchlist(user_id, watchlist_id)
        self.watchlist_repository.delete(watchlist)

    def add_company(
        self,
        user_id: int,
        watchlist_id: int,
        company_id: int,
    ) -> None:
        watchlist = self.get_watchlist(user_id, watchlist_id)

        company = self.company_repository.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError(company_id)

        if self.watchlist_repository.company_exists(
            watchlist.id,
            company.id,
        ):
            raise CompanyAlreadyInWatchlistError(company.symbol)

        self.watchlist_repository.add_company(
            watchlist.id,
            company.id,
        )

    def remove_company(
        self,
        user_id: int,
        watchlist_id: int,
        company_id: int,
    ) -> None:
        watchlist = self.get_watchlist(user_id, watchlist_id)

        company = self.company_repository.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError(company_id)

        removed = self.watchlist_repository.remove_company(
            watchlist.id,
            company.id,
        )

        if not removed:
            raise CompanyNotInWatchlistError(company.symbol)
