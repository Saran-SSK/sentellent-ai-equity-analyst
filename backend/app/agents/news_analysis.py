from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.providers.gemini_provider import gemini_provider

logger = logging.getLogger(__name__)


class NewsAnalysis(BaseModel):
    """Structured output for news analysis."""

    sentiment: str = Field(
        default="Neutral",
        description="Market sentiment: Bullish, Neutral, or Bearish",
    )
    impact: str = Field(
        default="Low",
        description="Market impact: High, Medium, or Low",
    )
    event_type: str = Field(
        default="Other",
        description="Type of news event: Earnings, Guidance, Product Launch, Acquisition, Partnership, Regulation, Management, Litigation, Macroeconomics, or Other",
    )
    mentioned_companies: list[str] = Field(
        default_factory=list,
        description="List of stock tickers or company names explicitly mentioned in the news",
    )


class NewsAnalysisAgent:
    """Analyzes news articles and extracts structured metadata."""

    # Allowed enum values for validation
    ALLOWED_SENTIMENTS = {
        "Bullish",
        "Neutral",
        "Bearish",
    }
    ALLOWED_IMPACTS = {
        "High",
        "Medium",
        "Low",
    }
    ALLOWED_EVENT_TYPES = {
        "Earnings",
        "Guidance",
        "Product Launch",
        "Acquisition",
        "Partnership",
        "Regulation",
        "Management",
        "Litigation",
        "Macroeconomics",
        "Other",
    }

    # System prompt as class constant
    SYSTEM_PROMPT = """You are a financial news analysis assistant.

Your task is to analyze a news article and extract structured metadata.

Rules:

- Extract ONLY explicit information from the headline and summary.
- NEVER invent companies that are not mentioned in the text.
- If sentiment is uncertain, default to Neutral.
- If impact is uncertain, default to Low.
- If event type is uncertain, default to Other.
- Return ONLY valid JSON."""

    def __init__(self) -> None:
        self._llm = gemini_provider.get_llm()

    def analyze(
        self,
        headline: str,
        summary: str,
    ) -> dict[str, Any]:
        """Analyze a news article and extract structured metadata.

        Args:
            headline: The news article headline.
            summary: The news article summary.

        Returns:
            Dictionary with sentiment, impact, event_type, and mentioned_companies.
        """
        if not headline or not headline.strip():
            return self._get_default_response()

        human_prompt = f"""Analyze this news article:

Headline: {headline}

Summary: {summary if summary else "No summary provided."}

Return ONLY valid JSON with these fields:
- sentiment (Bullish, Neutral, Bearish)
- impact (High, Medium, Low)
- event_type (Earnings, Guidance, Product Launch, Acquisition, Partnership, Regulation, Management, Litigation, Macroeconomics, Other)
- mentioned_companies (list of stock tickers or company names explicitly mentioned)"""

        try:
            # Try structured output first
            structured_llm = self._llm.with_structured_output(NewsAnalysis)
            result: NewsAnalysis = structured_llm.invoke(
                [
                    SystemMessage(content=self.SYSTEM_PROMPT),
                    HumanMessage(content=human_prompt),
                ]
            )

            # Validate and normalize
            return self._validate_and_normalize(
                {
                    "sentiment": result.sentiment,
                    "impact": result.impact,
                    "event_type": result.event_type,
                    "mentioned_companies": result.mentioned_companies,
                }
            )

        except Exception as e:
            logger.warning(f"Structured output analysis failed: {e}. Returning default response.")
            return self._get_default_response()

    def _get_default_response(self) -> dict[str, Any]:
        """Return default response when analysis fails."""
        return {
            "sentiment": "Neutral",
            "impact": "Low",
            "event_type": "Other",
            "mentioned_companies": [],
        }

    def _validate_and_normalize(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize extracted values."""
        validated = {}

        # Validate sentiment
        sentiment = analysis.get("sentiment", "Neutral")
        if sentiment in self.ALLOWED_SENTIMENTS:
            validated["sentiment"] = sentiment
        else:
            logger.debug(f"Discarding invalid sentiment: {sentiment}, using Neutral")
            validated["sentiment"] = "Neutral"

        # Validate impact
        impact = analysis.get("impact", "Low")
        if impact in self.ALLOWED_IMPACTS:
            validated["impact"] = impact
        else:
            logger.debug(f"Discarding invalid impact: {impact}, using Low")
            validated["impact"] = "Low"

        # Validate event_type
        event_type = analysis.get("event_type", "Other")
        if event_type in self.ALLOWED_EVENT_TYPES:
            validated["event_type"] = event_type
        else:
            logger.debug(f"Discarding invalid event_type: {event_type}, using Other")
            validated["event_type"] = "Other"

        # Validate mentioned_companies is a list
        companies = analysis.get("mentioned_companies", [])
        if isinstance(companies, list):
            # Filter to non-empty strings
            validated["mentioned_companies"] = [c for c in companies if c and c.strip()]
        else:
            logger.debug(f"mentioned_companies is not a list, using empty list")
            validated["mentioned_companies"] = []

        return validated
