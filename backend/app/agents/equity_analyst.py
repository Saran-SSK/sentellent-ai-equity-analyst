from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.providers.gemini_provider import gemini_provider
from app.rag.retrieval import retrieval_service


class DocumentType(Enum):
    """Document type enum for context-aware analysis."""
    ANNUAL_REPORT = "annual_report"
    NEWS = "news"
    MIXED = "mixed"
    NONE = "none"


class EquityAnalystAgent:
    """Context-aware AI agent for equity analysis questions."""

    def ask(
        self,
        question: str,
        company: str | None = None,
    ) -> str:
        """Answer an equity analysis question using retrieved context."""

        if not question.strip():
            raise ValueError("Question is required.")

        retrieved_chunks = retrieval_service.retrieve(
            query=question,
            company=company,
        )

        document_type = self._detect_document_type(retrieved_chunks)
        context = self._build_context(retrieved_chunks)
        sources = self._build_sources(retrieved_chunks)

        prompt = self._build_prompt(
            question=question,
            context=context,
            document_type=document_type,
            has_context=bool(retrieved_chunks),
        )

        response = gemini_provider.get_llm().invoke(prompt)

        if isinstance(response.content, str):
            answer = response.content.strip()
        elif isinstance(response.content, list):
            answer = "".join(
                item.get("text", "")
                for item in response.content
                if isinstance(item, dict)
            ).strip()
        else:
            answer = str(response.content).strip()

        # Append sources if available
        if sources:
            answer = f"{answer}\n\n## Sources\n\n{sources}"

        return answer

    def _detect_document_type(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> DocumentType:
        """Detect the type of documents retrieved."""
        if not retrieved_chunks:
            return DocumentType.NONE

        doc_types = {
            chunk.get("document_type", "")
            for chunk in retrieved_chunks
            if chunk.get("document_type")
        }

        if "annual_report" in doc_types and "news" in doc_types:
            return DocumentType.MIXED
        if "annual_report" in doc_types:
            return DocumentType.ANNUAL_REPORT
        if "news" in doc_types:
            return DocumentType.NEWS

        return DocumentType.NONE

    def _build_context(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        """Combine retrieved chunks with metadata into a rich context."""

        if not retrieved_chunks:
            return ""

        context_parts = []
        for chunk in retrieved_chunks:
            chunk_text = chunk.get("chunk", "")
            if not chunk_text:
                continue

            metadata_lines = []
            doc_type = chunk.get("document_type", "")
            if doc_type:
                metadata_lines.append(f"Document Type: {doc_type}")

            headline = chunk.get("headline", "")
            if headline:
                metadata_lines.append(f"Headline: {headline}")

            source = chunk.get("source", "")
            if source:
                metadata_lines.append(f"Source: {source}")

            published_at = chunk.get("published_at", "")
            if published_at:
                metadata_lines.append(f"Published: {published_at}")

            if metadata_lines:
                context_parts.append("\n".join(metadata_lines) + f"\n\n{chunk_text}")
            else:
                context_parts.append(chunk_text)

        return "\n\n".join(context_parts)

    def _build_sources(
        self,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        """Build a formatted sources list from retrieved chunks."""
        if not retrieved_chunks:
            return ""

        sources_seen = set()
        source_lines = []

        for chunk in retrieved_chunks:
            doc_type = chunk.get("document_type", "")
            source = chunk.get("source", "")
            published_at = chunk.get("published_at", "")

            if not source:
                continue

            # Create unique key for deduplication
            source_key = (doc_type, source, published_at)
            if source_key in sources_seen:
                continue
            sources_seen.add(source_key)

            if doc_type == "annual_report":
                source_lines.append(f"- {source}")
            elif doc_type == "news" and published_at:
                # Format date for news
                try:
                    date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%Y-%m-%d")
                    source_lines.append(f"- {source} ({date_str})")
                except (ValueError, AttributeError):
                    source_lines.append(f"- {source}")
            else:
                source_lines.append(f"- {source}")

        return "\n".join(source_lines) if source_lines else ""

    def _build_prompt(
        self,
        question: str,
        context: str,
        document_type: DocumentType,
        has_context: bool,
    ) -> list[SystemMessage | HumanMessage]:
        """Construct the prompt for Gemini based on document type."""

        system_prompt = self._get_system_prompt(document_type)

        if not has_context:
            system_prompt += """

No relevant company documents were retrieved.

Inform the user that no supporting documents were found before giving any general financial explanation.
"""

        human_prompt = f"""
Retrieved Company Documents

{context if context else "No relevant company documents found."}

User Question

{question}
"""

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

    def _get_system_prompt(self, document_type: DocumentType) -> str:
        """Get the appropriate system prompt based on document type."""

        if document_type == DocumentType.ANNUAL_REPORT:
            return self._annual_report_prompt()
        elif document_type == DocumentType.NEWS:
            return self._news_prompt()
        elif document_type == DocumentType.MIXED:
            return self._mixed_prompt()
        else:
            return self._annual_report_prompt()

    def _annual_report_prompt(self) -> str:
        """System prompt for annual report analysis."""
        return """
You are a Senior Equity Research Analyst.

Answer ONLY using the retrieved annual report documents.

Your response MUST follow EXACTLY this format.

## Summary

Write 2-3 concise sentences.

## Key Findings

- Bullet point
- Bullet point
- Bullet point

## Financial Highlights

- Revenue
- Profitability metrics
- Margins
- Business segments
- Growth percentages
- Other important financial metrics

## Risks

- Key risks mentioned in the report

## Outlook

- Company's forward-looking statements

## Conclusion

Write one short concluding paragraph.

Rules:

- Never invent facts.
- Never fabricate numbers.
- Use ONLY the retrieved context.
- If the answer is not present in the context, clearly state that.
- Never repeat the user's question.
- Never copy long passages from the report.
- Summarize naturally.
- Keep the response under 300 words.
"""

    def _news_prompt(self) -> str:
        """System prompt for news analysis."""
        return """
You are a Senior Equity Research Analyst.

Answer ONLY using the retrieved news articles.

Your response MUST follow EXACTLY this format.

## Summary

Write 2-3 concise sentences.

## Key Developments

- Recent developments
- Product launches
- Acquisitions
- Regulations
- Earnings announcements
- Analyst opinions

## Market Impact

- Likely business implications
- Stock market impact

## Risks

- Risks discussed in the news

## Opportunities

- Opportunities mentioned in the news

## Conclusion

Write one short concluding paragraph.

Rules:

- Never invent facts.
- Never fabricate numbers.
- Use ONLY the retrieved context.
- Do NOT ask for revenue tables unless present in the news.
- If the answer is not present in the context, clearly state that.
- Never repeat the user's question.
- Never copy long passages from the articles.
- Summarize naturally.
- Keep the response under 300 words.
"""

    def _mixed_prompt(self) -> str:
        """System prompt for mixed document analysis."""
        return """
You are a Senior Equity Research Analyst.

Answer using BOTH the retrieved annual reports and news articles.

Your response MUST follow EXACTLY this format.

## Summary

Write 2-3 concise sentences.

## Financial Fundamentals

- Revenue
- Profitability metrics
- Margins
- Business segments
- Growth percentages

## Recent Developments

- Recent news developments
- Product launches
- Acquisitions
- Regulations
- Earnings announcements

## Analysis

- Explain how recent news affects company fundamentals
- Combine financial data with latest developments

## Risks

- Risks from both annual reports and news

## Outlook

- Combined outlook based on fundamentals and recent news

## Conclusion

Write one short concluding paragraph.

Rules:

- Never invent facts.
- Never fabricate numbers.
- Use ONLY the retrieved context.
- Synthesize information from both document types.
- If the answer is not present in the context, clearly state that.
- Never repeat the user's question.
- Never copy long passages from the documents.
- Summarize naturally.
- Keep the response under 350 words.
"""


equity_analyst_agent = EquityAnalystAgent()
