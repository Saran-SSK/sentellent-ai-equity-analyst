from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.core.exceptions import ErrorResponse


def _build_error_response(request: Request, message: str, error: str, status_code: int) -> JSONResponse:
    payload = ErrorResponse(
        message=message,
        error=error,
        path=str(request.url.path),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    status_code = exc.status_code
    error = "not_found" if status_code == HTTP_404_NOT_FOUND else "http_exception"
    return _build_error_response(request, message, error, status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _build_error_response(
        request,
        "Invalid request data",
        "validation_error",
        HTTP_400_BAD_REQUEST,
    )


async def unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _build_error_response(
        request,
        "Internal server error",
        "unexpected_error",
        HTTP_500_INTERNAL_SERVER_ERROR,
    )
