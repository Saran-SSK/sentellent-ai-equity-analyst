from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PDFIngestionResponse(BaseModel):
    """Response returned after ingesting a PDF."""

    model_config = ConfigDict(from_attributes=True, extra="forbid", str_strip_whitespace=True)

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable ingestion status message.",
        examples=["PDF ingested successfully."],
    )
    chunks: int = Field(
        ...,
        ge=0,
        description="Number of PDF text chunks ingested.",
        examples=[42],
    )
