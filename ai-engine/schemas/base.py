"""Base schema classes and common data types for ARCANA AI Brain."""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


def generate_id(prefix: str = "arc") -> str:
    """Generate a unique ID with an optional prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def current_utc_time() -> datetime:
    """Return current timestamp in UTC timezone."""
    return datetime.now(timezone.utc)


class ArcanaBaseModel(BaseModel):
    """Base Pydantic model for ARCANA entities with standardized configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )
