from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base

engine = create_engine(str(settings.database_url), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

__all__ = ["engine", "SessionLocal", "Base"]
