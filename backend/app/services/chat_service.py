from __future__ import annotations

from app.agents.equity_analyst import equity_analyst_agent
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """Service layer for equity analyst chat operations."""

    async def ask(self, request: ChatRequest) -> ChatResponse:
        """Ask the equity analyst agent a company-specific question."""
        answer = equity_analyst_agent.ask(
            company=request.company,
            question=request.question,
        )
        return ChatResponse(answer=answer)


chat_service = ChatService()
