from __future__ import annotations

from unittest.mock import Mock

from app.agents.memory_extractor import MemoryExtractor


def test_extract_uses_lightweight_patterns_without_llm() -> None:
    extractor = object.__new__(MemoryExtractor)
    extractor._llm = Mock()
    extractor._llm.with_structured_output.side_effect = AssertionError(
        "LLM structured output should not be used for simple preference extraction"
    )
    extractor._llm.invoke.side_effect = AssertionError(
        "LLM invoke should not be used for simple preference extraction"
    )

    result = extractor.extract(
        "I am a conservative investor looking for long-term growth in healthcare."
    )

    assert result["risk_profile"] == "Conservative"
    assert result["investment_horizon"] == "Long Term"
    assert result["investment_style"] == "Growth"
    assert result["preferred_sectors"] == "Healthcare"


def test_extract_skips_llm_for_factual_questions() -> None:
    extractor = object.__new__(MemoryExtractor)
    extractor._llm = Mock()
    extractor._llm.with_structured_output.side_effect = AssertionError(
        "LLM structured output should not be used for factual questions"
    )
    extractor._llm.invoke.side_effect = AssertionError(
        "LLM invoke should not be used for factual questions"
    )

    result = extractor.extract("What is Apple's PE ratio?")

    assert result == {}
