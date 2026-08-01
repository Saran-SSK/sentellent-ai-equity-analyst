from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field, ConfigDict

from app.rag.retrieval import retrieval_service
from app.providers.gemini_provider import gemini_provider
from app.models.investor_profile import InvestorProfile

logger = logging.getLogger(__name__)


# Pydantic Models for Structured Output

class Recommendation(BaseModel):
    """A single stock recommendation with evaluation details."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    company: str = Field(
        ...,
        description="Company ticker symbol",
        examples=["TCS"],
    )
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Recommendation score from 0-100",
        examples=[85],
    )
    suitability: str = Field(
        ...,
        description="Suitability assessment (High/Medium/Low)",
        examples=["High"],
    )
    reason: str = Field(
        ...,
        description="Primary reason for recommendation",
        examples=["Strong fundamentals and growth potential"],
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Key risks associated with this investment",
        examples=["Market volatility", "Sector downturn"],
    )
    explanation: str = Field(
        ...,
        description="Detailed explanation of the recommendation",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Retrieved evidence supporting the recommendation",
    )
    citations: list[str] = Field(
        default_factory=list,
        description="Source citations for the evidence",
    )


class RecommendationResponse(BaseModel):
    """Response containing personalized stock recommendations."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    recommendations: list[Recommendation] = Field(
        ...,
        description="Top 5 stock recommendations",
    )
    investor_profile_summary: str = Field(
        ...,
        description="Summary of the investor profile used for recommendations",
    )


class RecommendationService:
    """Service for generating personalized stock recommendations based on investor profile and retrieved data."""

    # Candidate universe of Indian companies (easily extensible)
    INDIAN_COMPANIES = [
        "TCS",
        "INFY",
        "RELIANCE",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "LT",
        "ITC",
        "BHARTIARTL",
        "AXISBANK",
        "KOTAKBANK",
        "ASIANPAINT",
        "MARUTI",
        "SUNPHARMA",
        "TITAN",
    ]

    def __init__(self) -> None:
        """Initialize the recommendation service."""
        pass

    def get_recommendations(
        self,
        investor_profile: InvestorProfile,
    ) -> RecommendationResponse:
        """Generate personalized stock recommendations based on investor profile.

        Args:
            investor_profile: The user's investor profile containing risk tolerance,
                investment horizon, preferred sectors, etc.

        Returns:
            RecommendationResponse containing top 5 stock recommendations with
            explanations, evidence, and citations grounded in retrieved data.

        Raises:
            ValueError: If investor profile is invalid or no recommendations can be generated.
        """
        if not investor_profile:
            raise ValueError("Investor profile is required for recommendations")

        logger.info(f"Generating recommendations for user with risk profile: {investor_profile.risk_profile}")

        # Step 1: Build candidate universe based on investor preferences
        candidates = self._build_candidate_universe(investor_profile)
        logger.info(f"Built candidate universe with {len(candidates)} companies")

        # Step 2: Retrieve documents for ALL candidates first
        company_documents = {}
        for company in candidates:
            docs = self._retrieve_company_documents(company)
            company_documents[company] = docs
            logger.debug(f"Retrieved {len(docs)} documents for {company}")

        # Step 3: Filter out companies with insufficient evidence
        min_documents = 3  # Minimum documents to consider a company
        qualified_candidates = {
            company: docs
            for company, docs in company_documents.items()
            if len(docs) >= min_documents
        }
        logger.info(f"Qualified {len(qualified_candidates)} candidates with sufficient evidence")

        if not qualified_candidates:
            raise ValueError("No companies with sufficient data for recommendations")

        # Step 4: Rank candidates heuristically based on retrieved data
        ranked_candidates = self._rank_candidates_heuristically(
            candidates=qualified_candidates,
            investor_profile=investor_profile,
        )
        logger.info(f"Ranked candidates: {[c for c, _ in ranked_candidates]}")

        # Step 5: Take Top 5 for LLM evaluation
        top_5_candidates = ranked_candidates[:5]
        logger.info(f"Selected Top 5 for LLM evaluation: {[c for c, _ in top_5_candidates]}")

        # Step 6: Evaluate only Top 5 using LLM
        evaluations = []
        for company, _ in top_5_candidates:
            docs = company_documents.get(company, [])
            try:
                evaluation = self._evaluate_company(
                    company=company,
                    documents=docs,
                    investor_profile=investor_profile,
                )
                # Validate citations against retrieved documents
                validated_evaluation = self._validate_citations(
                    evaluation=evaluation,
                    documents=docs,
                )
                evaluations.append(validated_evaluation)
                logger.debug(f"Evaluated {company} with score {evaluation.score}")
            except Exception as e:
                logger.error(f"Failed to evaluate {company}: {e}")
                continue

        # Step 7: Final ranking by LLM score and return top 5
        evaluations.sort(key=lambda x: x.score, reverse=True)
        top_recommendations = evaluations[:5]

        # Step 8: Build response
        profile_summary = self._build_profile_summary(investor_profile)
        logger.info(f"Generated {len(top_recommendations)} recommendations")

        return RecommendationResponse(
            recommendations=top_recommendations,
            investor_profile_summary=profile_summary,
        )

    def _build_candidate_universe(
        self,
        investor_profile: InvestorProfile,
    ) -> list[str]:
        """Build a candidate universe based on investor preferences.

        Args:
            investor_profile: The user's investor profile

        Returns:
            List of company tickers to evaluate
        """
        candidates = self.INDIAN_COMPANIES.copy()

        # Filter by preferred market if specified
        if investor_profile.preferred_market:
            preferred_market = investor_profile.preferred_market.upper()
            if preferred_market == "NSE":
                # All our candidates are NSE, so no filtering needed
                pass
            elif preferred_market == "BSE":
                # Could add BSE-specific filtering in the future
                pass

        # Prioritize preferred sectors if specified
        if investor_profile.preferred_sectors:
            preferred_sectors = [
                s.strip().upper()
                for s in investor_profile.preferred_sectors.split(",")
                if s.strip()
            ]

            # Sector to company mapping (based on common knowledge)
            sector_mapping = {
                "IT": ["TCS", "INFY"],
                "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
                "INFRASTRUCTURE": ["LT", "RELIANCE"],
                "CONSUMER": ["ITC", "ASIANPAINT", "MARUTI", "TITAN"],
                "PHARMACEUTICAL": ["SUNPHARMA"],
                "TELECOM": ["BHARTIARTL"],
            }

            # Move companies in preferred sectors to the front
            prioritized = []
            others = []

            for sector in preferred_sectors:
                sector_companies = sector_mapping.get(sector.upper(), [])
                for company in sector_companies:
                    if company in candidates and company not in prioritized:
                        prioritized.append(company)

            for company in candidates:
                if company not in prioritized:
                    others.append(company)

            candidates = prioritized + others

        # Adjust for risk profile - influence ordering
        if investor_profile.risk_profile:
            risk_profile = investor_profile.risk_profile.lower()
            
            # Conservative: prioritize stable, large-cap companies
            if risk_profile == "conservative":
                stable_companies = ["TCS", "INFY", "HDFCBANK", "ICICIBANK", "RELIANCE", "ITC"]
                prioritized = []
                others = []
                
                for company in candidates:
                    if company in stable_companies:
                        prioritized.append(company)
                    else:
                        others.append(company)
                
                candidates = prioritized + others
            
            # Aggressive: prioritize growth companies
            elif risk_profile == "aggressive":
                growth_companies = ["BHARTIARTL", "MARUTI", "TITAN", "ASIANPAINT", "LT"]
                prioritized = []
                others = []
                
                for company in candidates:
                    if company in growth_companies:
                        prioritized.append(company)
                    else:
                        others.append(company)
                
                candidates = prioritized + others

        return candidates

    def _retrieve_company_documents(
        self,
        company: str,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant documents for a company.

        Args:
            company: Company ticker symbol

        Returns:
            List of retrieved document chunks with metadata
        """
        documents = []

        # Retrieve fundamentals documents
        try:
            fundamentals_docs = retrieval_service.retrieve(
                query=f"{company} fundamentals financial metrics",
                company=company,
                limit=5,
                score_threshold=0.3,
            )
            documents.extend(fundamentals_docs)
            logger.debug(f"Retrieved {len(fundamentals_docs)} fundamentals documents for {company}")
        except Exception as e:
            logger.warning(f"Failed to retrieve fundamentals for {company}: {e}")

        # Retrieve news documents
        try:
            news_docs = retrieval_service.retrieve(
                query=f"{company} recent news developments",
                company=company,
                limit=5,
                score_threshold=0.3,
            )
            documents.extend(news_docs)
            logger.debug(f"Retrieved {len(news_docs)} news documents for {company}")
        except Exception as e:
            logger.warning(f"Failed to retrieve news for {company}: {e}")

        # Retrieve annual report documents
        try:
            report_docs = retrieval_service.retrieve(
                query=f"{company} annual report financial performance",
                company=company,
                limit=5,
                score_threshold=0.3,
            )
            documents.extend(report_docs)
            logger.debug(f"Retrieved {len(report_docs)} annual report documents for {company}")
        except Exception as e:
            logger.warning(f"Failed to retrieve annual reports for {company}: {e}")

        return documents

    def _rank_candidates_heuristically(
        self,
        candidates: dict[str, list[dict[str, Any]]],
        investor_profile: InvestorProfile,
    ) -> list[tuple[str, float]]:
        """Rank candidates heuristically based on retrieved data.

        Args:
            candidates: Dictionary mapping company to retrieved documents
            investor_profile: User's investor profile

        Returns:
            List of (company, heuristic_score) tuples sorted by score descending
        """
        scored_candidates = []

        for company, docs in candidates.items():
            score = 0.0

            # Score based on document count (more documents = more data available)
            doc_count_score = min(len(docs) / 15.0, 1.0) * 20  # Max 20 points
            score += doc_count_score

            # Score based on document type diversity
            doc_types = set(doc.get("document_type", "") for doc in docs)
            diversity_score = len(doc_types) * 5  # Max 15 points (3 types)
            score += diversity_score

            # Score based on average retrieval score
            avg_retrieval_score = sum(doc.get("score", 0) for doc in docs) / len(docs) if docs else 0
            retrieval_score = avg_retrieval_score * 30  # Max 30 points
            score += retrieval_score

            # Score based on sector preference
            if investor_profile.preferred_sectors:
                preferred_sectors = [
                    s.strip().upper()
                    for s in investor_profile.preferred_sectors.split(",")
                    if s.strip()
                ]
                # Check if company is in preferred sector (using sector mapping)
                sector_mapping = {
                    "IT": ["TCS", "INFY"],
                    "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"],
                    "INFRASTRUCTURE": ["LT", "RELIANCE"],
                    "CONSUMER": ["ITC", "ASIANPAINT", "MARUTI", "TITAN"],
                    "PHARMACEUTICAL": ["SUNPHARMA"],
                    "TELECOM": ["BHARTIARTL"],
                }
                for sector, companies in sector_mapping.items():
                    if company in companies and sector in preferred_sectors:
                        score += 20  # Bonus for preferred sector
                        break

            # Score based on risk profile alignment
            if investor_profile.risk_profile:
                risk_profile = investor_profile.risk_profile.lower()
                stable_companies = ["TCS", "INFY", "HDFCBANK", "ICICIBANK", "RELIANCE", "ITC"]
                growth_companies = ["BHARTIARTL", "MARUTI", "TITAN", "ASIANPAINT", "LT"]
                
                if risk_profile == "conservative" and company in stable_companies:
                    score += 15  # Bonus for conservative-friendly companies
                elif risk_profile == "aggressive" and company in growth_companies:
                    score += 15  # Bonus for aggressive-friendly companies

            scored_candidates.append((company, score))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates

    def _validate_citations(
        self,
        evaluation: Recommendation,
        documents: list[dict[str, Any]],
    ) -> Recommendation:
        """Validate citations against retrieved documents.

        Args:
            evaluation: The LLM-generated recommendation
            documents: Retrieved documents for the company

        Returns:
            Recommendation with validated citations
        """
        # Extract available sources from documents
        available_sources = set(doc.get("source", "") for doc in documents)

        # Filter citations to only include those that match available sources
        validated_citations = [
            citation
            for citation in evaluation.citations
            if any(source in citation for source in available_sources)
        ]

        # Filter evidence to only include citations that were validated
        if validated_citations:
            validated_evidence = evaluation.evidence
        else:
            # If no valid citations, clear evidence to avoid hallucinations
            validated_evidence = []
            logger.warning(f"No valid citations found for {evaluation.company}, clearing evidence")

        # Return updated recommendation with validated citations
        return Recommendation(
            company=evaluation.company,
            score=evaluation.score,
            suitability=evaluation.suitability,
            reason=evaluation.reason,
            risks=evaluation.risks,
            explanation=evaluation.explanation,
            evidence=validated_evidence,
            citations=validated_citations,
        )

    def _evaluate_company(
        self,
        company: str,
        documents: list[dict[str, Any]],
        investor_profile: InvestorProfile,
    ) -> Recommendation:
        """Evaluate a company using LLM with structured output.

        Args:
            company: Company ticker symbol
            documents: Retrieved documents for the company
            investor_profile: User's investor profile

        Returns:
            Recommendation object with evaluation results
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            company=company,
            documents=documents,
            investor_profile=investor_profile,
        )

        # Get LLM with structured output
        llm = gemini_provider.get_llm()
        structured_llm = llm.with_structured_output(Recommendation)

        # Generate evaluation
        try:
            result = structured_llm.invoke(prompt)
            return result
        except Exception as e:
            logger.error(f"LLM evaluation failed for {company}: {e}")
            # Return a minimal recommendation on failure
            return Recommendation(
                company=company,
                score=50,
                suitability="Medium",
                reason="Evaluation failed - manual review recommended",
                risks=["Unable to assess due to evaluation failure"],
                explanation="Automated evaluation failed. Please review manually.",
                evidence=[],
                citations=[],
            )

    def _build_evaluation_prompt(
        self,
        company: str,
        documents: list[dict[str, Any]],
        investor_profile: InvestorProfile,
    ) -> str:
        """Build the evaluation prompt for LLM.

        Args:
            company: Company ticker symbol
            documents: Retrieved documents
            investor_profile: User's investor profile

        Returns:
            Formatted prompt string
        """
        # Build document context
        document_context = "\n\n".join(
            [
                f"Document {i+1} (Source: {doc.get('source', 'Unknown')}, Type: {doc.get('document_type', 'Unknown')}):\n{doc.get('chunk', '')}"
                for i, doc in enumerate(documents[:10])  # Limit to top 10 docs to avoid context overflow
            ]
        )

        # Build investor profile context
        profile_context = f"""
Risk Profile: {investor_profile.risk_profile or 'Not specified'}
Investment Horizon: {investor_profile.investment_horizon or 'Not specified'}
Investment Style: {investor_profile.investment_style or 'Not specified'}
Preferred Market: {investor_profile.preferred_market or 'Not specified'}
Preferred Sectors: {investor_profile.preferred_sectors or 'Not specified'}
"""

        prompt = f"""You are an expert equity analyst specializing in Indian stock markets. Evaluate the following company for investment suitability based on the provided documents and investor profile.

COMPANY: {company}

INVESTOR PROFILE:
{profile_context}

RETRIEVED DOCUMENTS:
{document_context}

INSTRUCTIONS:
1. Evaluate the company's quality based on fundamentals, recent news, and financial performance.
2. Assess compatibility with the investor's risk profile, investment horizon, and preferences.
3. Identify key risks and opportunities.
4. Provide a score from 0-100 (higher = better recommendation).
5. Determine suitability (High/Medium/Low).
6. Provide a clear reason for your recommendation.
7. List specific risks.
8. Write a detailed explanation.
9. Extract supporting evidence from the retrieved documents ONLY.
10. Provide citations for each piece of evidence (use document sources).

CRITICAL:
- ONLY use information from the retrieved documents above.
- DO NOT hallucinate or invent company information.
- DO NOT perform financial calculations outside of what's in the documents.
- If information is missing, state that it's not available in the documents.
- Ground all claims in the retrieved evidence.
- Prioritize Indian market context.

Return your evaluation as a structured Recommendation object.
"""

        return prompt

    def _build_profile_summary(
        self,
        investor_profile: InvestorProfile,
    ) -> str:
        """Build a summary of the investor profile.

        Args:
            investor_profile: The user's investor profile

        Returns:
            Formatted summary string
        """
        return (
            f"Risk Profile: {investor_profile.risk_profile or 'Not specified'}, "
            f"Investment Horizon: {investor_profile.investment_horizon or 'Not specified'}, "
            f"Investment Style: {investor_profile.investment_style or 'Not specified'}, "
            f"Preferred Market: {investor_profile.preferred_market or 'Not specified'}, "
            f"Preferred Sectors: {investor_profile.preferred_sectors or 'Not specified'}"
        )


recommendation_service = RecommendationService()
