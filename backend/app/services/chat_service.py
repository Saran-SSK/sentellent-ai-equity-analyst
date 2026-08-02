from __future__ import annotations

import logging

from app.agents.context_builder import ContextBuilder
from app.agents.equity_analyst import EquityAnalystAgent
from app.agents.memory_extractor import MemoryExtractor
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.investor_profile import InvestorProfileUpdate
from app.services.investor_profile import InvestorProfileService

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for equity analyst chat operations."""

    def __init__(
        self,
        context_builder: ContextBuilder,
        memory_extractor: MemoryExtractor,
        investor_profile_service: InvestorProfileService,
        equity_analyst_agent: EquityAnalystAgent,
    ) -> None:
        self.context_builder = context_builder
        self.memory_extractor = memory_extractor
        self.investor_profile_service = investor_profile_service
        self.equity_analyst_agent = equity_analyst_agent

    async def ask(self, request: ChatRequest, user_id: int) -> ChatResponse:
        """Ask the equity analyst agent a company-specific question."""
        # Extract investor preferences from the question
        extracted = self.memory_extractor.extract(request.question)

        # Update investor profile if preferences were extracted
        if extracted:
            self._update_investor_profile(user_id, extracted)

        # Build user context
        user_context = self.context_builder.build(
            user_id=user_id,
            company=request.company,
        )

        answer = self.equity_analyst_agent.ask(
            company=request.company,
            question=request.question,
            user_context=user_context,
        )
        return ChatResponse(answer=answer)

    def _update_investor_profile(
        self,
        user_id: int,
        extracted: dict[str, str],
    ) -> None:
        """Update investor profile with extracted preferences."""
        try:
            # Load existing profile
            existing_profile = self.investor_profile_service.get_profile(user_id)

            # Merge extracted fields with existing profile
            # Never overwrite existing values with None
            update_data = InvestorProfileUpdate()

            if extracted.get("risk_profile") is not None:
                update_data.risk_profile = extracted["risk_profile"]
            elif existing_profile and existing_profile.risk_profile:
                update_data.risk_profile = existing_profile.risk_profile

            if extracted.get("investment_horizon") is not None:
                update_data.investment_horizon = extracted["investment_horizon"]
            elif existing_profile and existing_profile.investment_horizon:
                update_data.investment_horizon = existing_profile.investment_horizon

            if extracted.get("investment_style") is not None:
                update_data.investment_style = extracted["investment_style"]
            elif existing_profile and existing_profile.investment_style:
                update_data.investment_style = existing_profile.investment_style

            if extracted.get("preferred_market") is not None:
                update_data.preferred_market = extracted["preferred_market"]
            elif existing_profile and existing_profile.preferred_market:
                update_data.preferred_market = existing_profile.preferred_market

            if extracted.get("preferred_sectors") is not None:
                update_data.preferred_sectors = extracted["preferred_sectors"]
            elif existing_profile and existing_profile.preferred_sectors:
                update_data.preferred_sectors = existing_profile.preferred_sectors

            if extracted.get("notes") is not None:
                update_data.notes = extracted["notes"]
            elif existing_profile and existing_profile.notes:
                update_data.notes = existing_profile.notes

            # Persist updated profile
            self.investor_profile_service.upsert_profile(user_id, update_data)

            # Log the update
            updated_fields = [f"{k} -> {v}" for k, v in extracted.items()]
            logger.info(f"Updated investor memory for user {user_id}: {', '.join(updated_fields)}")

        except Exception as e:
            logger.error(f"Failed to update investor profile for user {user_id}: {e}")

