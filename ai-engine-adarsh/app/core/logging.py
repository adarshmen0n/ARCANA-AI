"""Structured Logging for ARCANA-AI Brain.

Supports operational tracking, request IDs, latency measurement, and clean output.
"""

import logging
import sys
from typing import Optional
from .config import settings


class ArcanaFormatter(logging.Formatter):
    """Custom formatter providing clear, contextual log lines."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def setup_logging() -> None:
    """Configures the root and application loggers."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = ArcanaFormatter(
        fmt="%(asctime)s | %(levelname)-7s | [%(request_id)s] %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)

    # Suppress overly noisy logs from third-party libraries if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str, request_id: Optional[str] = None) -> logging.LoggerAdapter:
    """Returns a logger adapter with contextual request_id support."""
    logger = logging.getLogger(name)
    extra = {"request_id": request_id or "-"}
    return logging.LoggerAdapter(logger, extra)
