from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_context_builder
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Ask an equity analyst question",
    description="Ask the AI equity analyst a company-specific question.",
)
async def ask_question(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    context_builder: Annotated[
        "app.agents.context_builder.ContextBuilder",
        Depends(get_context_builder),
    ],
) -> ChatResponse:
    """Ask the equity analyst assistant a question about a company."""
    chat_service = ChatService(context_builder)
    return await chat_service.ask(request, current_user.id)
