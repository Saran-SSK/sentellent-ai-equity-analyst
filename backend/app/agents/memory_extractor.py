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
        self._llm = gemini_provider.get_llm()

    def extract(self, message: str) -> dict[str, str | None]:
        """Extract investor preferences from a user message.

        Args:
            message: The user's message to analyze.

        Returns:
            Dictionary with extracted preferences. Returns empty dict if no preferences found.
        """
        if not message or not message.strip():
            return {}

        human_prompt = f"""Extract investor preferences from this message:

{message}

Return ONLY valid JSON. Return {{}} if no preferences should be remembered."""

        try:
            # Try structured output first
            structured_llm = self._llm.with_structured_output(MemoryExtraction)
            result: MemoryExtraction = structured_llm.invoke(
                [
                    SystemMessage(content=self.SYSTEM_PROMPT),
                    HumanMessage(content=human_prompt),
                ]
            )

            # Convert to dict and filter out None values
            extracted = {
                "risk_profile": result.risk_profile,
                "investment_horizon": result.investment_horizon,
                "investment_style": result.investment_style,
                "preferred_market": result.preferred_market,
                "preferred_sectors": result.preferred_sectors,
                "notes": result.notes,
            }

            # Validate and normalize enum values
            return self._validate_and_normalize(extracted)

        except Exception as e:
            logger.warning(f"Structured output extraction failed: {e}. Falling back to text-based extraction.")
            return self._fallback_extraction(human_prompt)

    def _fallback_extraction(self, human_prompt: str) -> dict[str, str | None]:
        """Fallback to text-based extraction when structured output fails."""
        try:
            response = self._llm.invoke(
                [
                    SystemMessage(content=self.SYSTEM_PROMPT),
                    HumanMessage(content=human_prompt),
                ]
            )

            if isinstance(response.content, str):
                content = response.content.strip()
                # Strip markdown code fences if present
                if content.startswith("```"):
                    content = content.strip("`")
                    # Remove language identifier if present (e.g., "json")
                    lines = content.split("\n")
                    if lines[0].strip().lower() in ["json", "{"]:
                        content = "\n".join(lines[1:])
                    content = content.strip()

                # Try to parse as JSON
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        # Filter to only allowed keys and non-null values
                        allowed_keys = {
                            "risk_profile",
                            "investment_horizon",
                            "investment_style",
                            "preferred_market",
                            "preferred_sectors",
                            "notes",
                        }
                        filtered = {
                            k: v
                            for k, v in parsed.items()
                            if k in allowed_keys and v is not None
                        }
                        # Validate and normalize
                        return self._validate_and_normalize(filtered)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from fallback response: {e}")

        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")

        # Return empty dict on any failure
        return {}

    def _validate_and_normalize(self, extracted: dict[str, str | None]) -> dict[str, str | None]:
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
