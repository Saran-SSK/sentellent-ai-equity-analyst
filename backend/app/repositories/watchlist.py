from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.watchlist import Watchlist, WatchlistCompany
from app.schemas.watchlist import WatchlistCreate


class WatchlistRepository:
    """Database operations for watchlists."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, watchlist_id: int) -> Watchlist | None:
        statement = (
            select(Watchlist)
            .options(
                selectinload(Watchlist.companies).selectinload(WatchlistCompany.company)
            )
            .where(Watchlist.id == watchlist_id)
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_id_for_user(
        self,
        watchlist_id: int,
        user_id: int,
    ) -> Watchlist | None:

        statement = (
            select(Watchlist)
            .options(
                selectinload(Watchlist.companies).selectinload(WatchlistCompany.company)
            )
            .where(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id,
            )
        )

        return self.session.execute(statement).scalar_one_or_none()

    def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Watchlist]:

        statement = (
            select(Watchlist)
            .options(
                selectinload(Watchlist.companies).selectinload(WatchlistCompany.company)
            )
            .where(Watchlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Watchlist.id)
        )

        return list(self.session.execute(statement).scalars().all())

    def create(
        self,
        user_id: int,
        watchlist: WatchlistCreate,
    ) -> Watchlist:

        db_watchlist = Watchlist(
            user_id=user_id,
            **watchlist.model_dump(),
        )

        self.session.add(db_watchlist)
        self.session.commit()
        self.session.refresh(db_watchlist)

        return db_watchlist

    def delete(self, watchlist: Watchlist) -> None:
        self.session.delete(watchlist)
        self.session.commit()

    def company_exists(
        self,
        watchlist_id: int,
        company_id: int,
    ) -> bool:

        statement = select(WatchlistCompany).where(
            WatchlistCompany.watchlist_id == watchlist_id,
            WatchlistCompany.company_id == company_id,
        )

        return self.session.execute(statement).scalar_one_or_none() is not None

    def add_company(
        self,
        watchlist_id: int,
        company_id: int,
    ) -> WatchlistCompany:

        association = WatchlistCompany(
            watchlist_id=watchlist_id,
            company_id=company_id,
        )

        self.session.add(association)
        self.session.commit()
        self.session.refresh(association)

        return association

    def remove_company(
        self,
        watchlist_id: int,
        company_id: int,
    ) -> bool:

        statement = select(WatchlistCompany).where(
            WatchlistCompany.watchlist_id == watchlist_id,
            WatchlistCompany.company_id == company_id,
        )

        association = self.session.execute(statement).scalar_one_or_none()

        if association is None:
            return False

        self.session.delete(association)
        self.session.commit()

        return True
