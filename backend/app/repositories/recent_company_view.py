from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.recent_company_view import UserCompanyView


class RecentCompanyViewRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_view(self, user_id: int, symbol: str) -> None:
        normalized_symbol = symbol.strip().upper()

        statement = select(UserCompanyView).where(
            UserCompanyView.user_id == user_id,
            UserCompanyView.symbol == normalized_symbol,
        )
        existing_view = self.session.execute(statement).scalar_one_or_none()

        if existing_view is not None:
            existing_view.viewed_at = datetime.now(timezone.utc)
            self.session.commit()
            return

        view = UserCompanyView(user_id=user_id, symbol=normalized_symbol)
        self.session.add(view)
        self.session.commit()

    def get_recent_symbols(self, user_id: int, limit: int = 10) -> list[str]:
        recent_views = (
            select(
                UserCompanyView.symbol,
                UserCompanyView.viewed_at,
                func.row_number()
                .over(
                    partition_by=UserCompanyView.symbol,
                    order_by=UserCompanyView.viewed_at.desc(),
                )
                .label("row_num"),
            )
            .where(UserCompanyView.user_id == user_id)
            .subquery()
        )

        statement = (
            select(recent_views.c.symbol)
            .where(recent_views.c.row_num == 1)
            .order_by(recent_views.c.viewed_at.desc(), recent_views.c.symbol)
            .limit(limit)
        )

        rows = self.session.execute(statement).scalars().all()
        return [symbol for symbol in rows if symbol]
