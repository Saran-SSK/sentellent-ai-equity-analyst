from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class GeminiProvider:
    """Provider for a configured Gemini chat model."""

    def __init__(self) -> None:
        """Initialize the Gemini LLM once for reuse."""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required to initialize GeminiProvider.")

        self._llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0.2,
            timeout=60,
            google_api_key=settings.gemini_api_key,
        )

    def get_llm(self) -> ChatGoogleGenerativeAI:
        """Return the initialized Gemini chat model."""
        return self._llm


gemini_provider = GeminiProvider()
