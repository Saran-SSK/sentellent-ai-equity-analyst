from __future__ import annotations

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Ask an equity analyst question",
    description="Ask the AI equity analyst a company-specific question.",
)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Ask the equity analyst assistant a question about a company."""
    return await chat_service.ask(request)
