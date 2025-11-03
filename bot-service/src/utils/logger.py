"""Structured logging configuration."""

import logging
import sys
from typing import Any

from .config import get_settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup structured logger with configuration from settings."""
    settings = get_settings()

    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)

    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def log_expense_processing(
    logger: logging.Logger,
    user_id: int,
    message: str,
    result: dict[str, Any] | None = None,
) -> None:
    """Log expense processing with structured data."""
    log_data = {
        "user_id": user_id,
        "message": message,
    }

    if result:
        log_data.update(result)

    logger.info(f"Expense processing: {log_data}")
