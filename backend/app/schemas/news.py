from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class NewsIngestionRequest(BaseModel):
    """Request payload for ingesting company news."""

    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True
    )

    company: str = Field(
        ...,
        min_length=1,
        description="Ticker symbol for the company whose news should be ingested.",
        examples=["AAPL"],
    )
    from_date: date = Field(
        ...,
        description="Inclusive start date for the news window.",
    )
    to_date: date = Field(
        ...,
        description="Inclusive end date for the news window.",
    )


class NewsIngestionResponse(BaseModel):
    """Response returned after ingesting company news."""

    model_config = ConfigDict(
        from_attributes=True, extra="forbid", str_strip_whitespace=True
    )

    company: str = Field(
        ...,
        min_length=1,
        description="Normalized company symbol.",
        examples=["AAPL"],
    )
    articles_ingested: int = Field(
        ...,
        ge=0,
        description="Number of news articles ingested.",
        examples=[10],
    )
    chunks_created: int = Field(
        ...,
        ge=0,
        description="Number of text chunks created and stored.",
        examples=[20],
    )
    status: str = Field(
        ...,
        min_length=1,
        description="Outcome of the ingestion attempt.",
        examples=["success"],
    )
