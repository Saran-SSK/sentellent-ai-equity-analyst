from __future__ import annotations

import logging
import os

try:
    from app.core.config import settings as app_settings
except Exception:  # pragma: no cover - fallback if config dependencies are unavailable
    app_settings = None


def _resolve_log_level() -> int:
    """Resolve the log level from app settings or environment variables."""
    if app_settings is not None:
        try:
            configured_level = getattr(app_settings, "log_level", None)
            if configured_level:
                return getattr(logging, str(configured_level).upper(), logging.INFO)
        except Exception:
            pass

    configured_level = os.getenv("LOG_LEVEL", "INFO")
    return getattr(logging, str(configured_level).upper(), logging.INFO)


def get_logger(name: str | None = None) -> logging.Logger:
    """Create and configure a module logger with consistent formatting."""
    logger = logging.getLogger(name or "app")
    if not logger.handlers:
        logger.setLevel(_resolve_log_level())
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def configure_logging() -> logging.Logger:
    """Initialize application logging configuration."""
    logger = get_logger("app.main")
    logger.setLevel(_resolve_log_level())
    return logger
