from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.providers.gemini_provider import gemini_provider

logger = logging.getLogger(__name__)


class MemoryExtraction(BaseModel):
    """Structured output for memory extraction."""

    risk_profile: str | None = Field(
        default=None,
        description="User's risk profile (e.g., Conservative, Moderate, Aggressive, Very Aggressive)",
    )
    investment_horizon: str | None = Field(
        default=None,
        description="User's investment horizon (e.g., Short Term, Medium Term, Long Term, Very Long Term)",
    )
    investment_style: str | None = Field(
        default=None,
        description="User's investment style (e.g., Value, Growth, Dividend, Index, Technical)",
    )
    preferred_market: str | None = Field(
        default=None,
        description="User's preferred market (e.g., NSE, NYSE, NASDAQ)",
    )
    preferred_sectors: str | None = Field(
        default=None,
        description="User's preferred sectors (e.g., IT, Banking, Healthcare)",
    )
    notes: str | None = Field(
        default=None,
        description="Additional investment preferences or constraints",
    )


class MemoryExtractor:
    """Extracts investor preferences from user messages."""

    # Allowed enum values for validation
    ALLOWED_RISK_PROFILES = {
        "Conservative",
        "Moderate",
        "Aggressive",
        "Very Aggressive",
    }
    ALLOWED_INVESTMENT_STYLES = {
        "Value",
        "Growth",
        "Dividend",
        "Index",
        "Technical",
    }
    ALLOWED_INVESTMENT_HORIZONS = {
        "Short Term",
        "Medium Term",
        "Long Term",
        "Very Long Term",
    }

    # System prompt as class constant
    SYSTEM_PROMPT = """You are an investment preference extraction assistant.

Your task is to analyze the user's message and extract explicit investor preferences.

Rules:

- Extract ONLY explicit user preferences mentioned in the message.
- For investment horizon ONLY: you may infer from common financial goals (e.g., "retirement" -> Long Term, "education" -> Medium Term, "emergency fund" -> Short Term).
- Do NOT infer any other fields (risk profile, investment style, market, sectors, notes).
- NEVER invent information not present in the message.
- Return empty JSON ({}) when no investor preferences should be remembered.
- Focus on: risk profile, investment horizon, investment style, preferred market, preferred sectors, and notes.
- If the user asks a factual question about a company (e.g., "What is Apple's PE ratio?"), return {}."""

    def __init__(self) -> None:
        self._llm = None

    def extract(self, message: str) -> dict[str, str | None]:
        """Extract investor preferences from a user message without another Gemini call.

        For common preference cues, this uses a lightweight rule-based pass that is fast,
        deterministic, and suitable for optional memory extraction. Complex cases remain
        unsupported rather than triggering an additional model request.
        """
        if not message or not message.strip():
            return {}

        normalized_message = message.strip()
        if self._looks_like_factual_question(normalized_message):
            return {}

        extracted = self._extract_with_rules(normalized_message)
        return self._validate_and_normalize(extracted)

    def _looks_like_factual_question(self, message: str) -> bool:
        """Return True for simple factual questions that should not influence memory."""
        lowered = message.lower()
        if not lowered.endswith("?"):
            return False

        return any(
            phrase in lowered
            for phrase in [
                "what is",
                "what are",
                "who is",
                "when did",
                "where is",
                "which company",
                "what does",
                "how much",
                "what was",
            ]
        )

    def _extract_with_rules(self, message: str) -> dict[str, str | None]:
        """Extract obvious investor preferences from a message with regex-based heuristics."""
        text = message.lower()
        extracted: dict[str, str | None] = {}

        if any(term in text for term in ["conservative", "risk averse", "low risk"]):
            extracted["risk_profile"] = "Conservative"
        elif any(term in text for term in ["moderate", "balanced", "medium risk"]):
            extracted["risk_profile"] = "Moderate"
        elif any(
            term in text for term in ["aggressive", "high risk", "growth oriented"]
        ):
            extracted["risk_profile"] = "Aggressive"
        elif any(
            term in text for term in ["very aggressive", "very risky", "speculative"]
        ):
            extracted["risk_profile"] = "Very Aggressive"

        if any(
            term in text
            for term in ["long term", "long-term", "retirement", "for the long run"]
        ):
            extracted["investment_horizon"] = "Long Term"
        elif any(
            term in text
            for term in ["medium term", "medium-term", "education", "college"]
        ):
            extracted["investment_horizon"] = "Medium Term"
        elif any(
            term in text
            for term in ["short term", "short-term", "emergency fund", "soon"]
        ):
            extracted["investment_horizon"] = "Short Term"

        if any(term in text for term in ["growth", "growth stock", "growth investing"]):
            extracted["investment_style"] = "Growth"
        elif any(term in text for term in ["value", "value investing", "undervalued"]):
            extracted["investment_style"] = "Value"
        elif any(term in text for term in ["dividend", "income"]):
            extracted["investment_style"] = "Dividend"
        elif any(term in text for term in ["index fund", "index", "etf"]):
            extracted["investment_style"] = "Index"
        elif any(term in text for term in ["technical", "chart", "momentum"]):
            extracted["investment_style"] = "Technical"

        if any(term in text for term in ["nyse", "new york stock exchange"]):
            extracted["preferred_market"] = "NYSE"
        elif any(term in text for term in ["nasdaq"]):
            extracted["preferred_market"] = "NASDAQ"
        elif any(term in text for term in ["nse", "national stock exchange", "india"]):
            extracted["preferred_market"] = "NSE"

        sector_mapping = {
            "healthcare": "Healthcare",
            "health care": "Healthcare",
            "banking": "Banking",
            "bank": "Banking",
            "it": "IT",
            "technology": "IT",
            "tech": "IT",
            "energy": "Energy",
            "financials": "Financials",
            "consumer": "Consumer",
            "telecom": "Telecommunications",
            "telecommunications": "Telecommunications",
        }
        for keyword, mapped_value in sector_mapping.items():
            if keyword in text:
                extracted["preferred_sectors"] = mapped_value
                break

        if any(
            term in text
            for term in ["avoid", "prefer not", "only invest in", "interested in"]
        ):
            extracted["notes"] = message.strip()

        return extracted

    def _validate_and_normalize(
        self, extracted: dict[str, str | None]
    ) -> dict[str, str | None]:
        """Validate and normalize extracted enum values."""
        validated = {}

        # Validate risk profile
        if extracted.get("risk_profile"):
            risk = extracted["risk_profile"]
            if risk in self.ALLOWED_RISK_PROFILES:
                validated["risk_profile"] = risk
            else:
                logger.debug(f"Discarding invalid risk_profile: {risk}")

        # Validate investment horizon
        if extracted.get("investment_horizon"):
            horizon = extracted["investment_horizon"]
            if horizon in self.ALLOWED_INVESTMENT_HORIZONS:
                validated["investment_horizon"] = horizon
            else:
                logger.debug(f"Discarding invalid investment_horizon: {horizon}")

        # Validate investment style
        if extracted.get("investment_style"):
            style = extracted["investment_style"]
            if style in self.ALLOWED_INVESTMENT_STYLES:
                validated["investment_style"] = style
            else:
                logger.debug(f"Discarding invalid investment_style: {style}")

        # Keep other fields as-is (preferred_market, preferred_sectors, notes)
        if extracted.get("preferred_market"):
            validated["preferred_market"] = extracted["preferred_market"]
        if extracted.get("preferred_sectors"):
            validated["preferred_sectors"] = extracted["preferred_sectors"]
        if extracted.get("notes"):
            validated["notes"] = extracted["notes"]

        return validated
