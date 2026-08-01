from __future__ import annotations

from app.agents.context_builder import ContextBuilder
from app.agents.equity_analyst import equity_analyst_agent
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    """Service layer for equity analyst chat operations."""

    def __init__(self, context_builder: ContextBuilder) -> None:
        self.context_builder = context_builder

    async def ask(self, request: ChatRequest, user_id: int) -> ChatResponse:
        """Ask the equity analyst agent a company-specific question."""
        # Build user context
        user_context = self.context_builder.build(
            user_id=user_id,
            company=request.company,
        )

        answer = equity_analyst_agent.ask(
            company=request.company,
            question=request.question,
            user_context=user_context,
        )
        return ChatResponse(answer=answer)
