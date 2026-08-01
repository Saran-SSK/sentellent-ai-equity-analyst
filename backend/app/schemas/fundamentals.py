from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FundamentalsIngestionRequest(BaseModel):
    """Request payload for ingesting company fundamentals."""

    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True
    )

    company: str = Field(
        ...,
        min_length=1,
        description="Ticker symbol for the company whose fundamentals should be ingested.",
        examples=["TCS", "RELIANCE", "INFY"],
    )


class FundamentalsIngestionResponse(BaseModel):
    """Response returned after ingesting company fundamentals."""

    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True
    )

    company: str = Field(
        ...,
        min_length=1,
        description="Normalized company symbol.",
        examples=["TCS"],
    )
    chunks_created: int = Field(
        ...,
        ge=0,
        description="Number of text chunks created and stored.",
        examples=[3],
    )
    status: str = Field(
        ...,
        min_length=1,
        description="Outcome of the ingestion attempt.",
        examples=["success"],
    )
