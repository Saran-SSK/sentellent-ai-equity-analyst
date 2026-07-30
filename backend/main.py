from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.handlers import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="Sentellent AI Equity Analyst",
    version="1.0.0",
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Sentellent AI Equity Analyst Backend is Running 🚀"}
