from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvestorProfile(Base):
    """Investor profile model for user investment preferences."""

    __tablename__ = "investor_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    risk_profile: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    investment_horizon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    investment_style: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    preferred_market: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    preferred_sectors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="investor_profile")
