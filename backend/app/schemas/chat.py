from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Fields accepted when asking a chat question."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    company: str = Field(
        ...,
        min_length=1,
        description="Company name or ticker symbol to analyze.",
        examples=["AAPL"],
    )
    question: str = Field(
        ...,
        min_length=1,
        description="Question to answer about the company.",
        examples=["What are the key growth drivers for Apple?"],
    )


class ChatResponse(BaseModel):
    """Answer returned by the chat endpoint."""

    model_config = ConfigDict(from_attributes=True, extra="forbid", str_strip_whitespace=True)

    answer: str = Field(
        ...,
        min_length=1,
        description="Generated answer to the requested company question.",
        examples=["Apple's growth is driven by services, ecosystem retention, and product refresh cycles."],
    )
