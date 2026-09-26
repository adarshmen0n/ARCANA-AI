"""Error handling and structured exception models for ARCANA-AI Brain.

Ensures zero stack trace leakage to users and strictly typed error envelopes.
"""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation")
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional structured debugging context")


class ArcanaErrorResponse(BaseModel):
    error: ErrorDetails


class ArcanaException(Exception):
    """Base exception for all domain errors within ARCANA-AI."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_AI_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(ArcanaException):
    """Raised when a requested document, student, or concept does not exist."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' was not found.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ValidationException(ArcanaException):
    """Raised when incoming educational content or telemetry fails schema validation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SCHEMA_VALIDATION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details=details,
        )


class ProviderUnavailableException(ArcanaException):
    """Raised when an external AI provider fails or exhausts retries."""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            message=f"AI Provider '{provider}' is currently unavailable: {reason}",
            code="PROVIDER_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"provider": provider, "reason": reason},
        )


async def arcana_exception_handler(request: Request, exc: ArcanaException) -> JSONResponse:
    """Handles all custom ArcanaException domain errors."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": request_id,
                "details": exc.details if exc.details else None,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled unexpected errors and returns a safe generic response."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the educational intelligence pipeline.",
                "request_id": request_id,
                "details": None,
            }
        },
    )
