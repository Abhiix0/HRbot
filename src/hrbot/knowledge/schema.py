"""
Knowledge Base Schema

Defines the canonical Pydantic v2 models for knowledge facts and retrieval results.
"""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KnowledgeEntry(BaseModel):
    """
    A single knowledge fact in the HR chatbot's knowledge base.
    
    Each entry answers a specific, narrowly-scoped question and is tagged
    with a fine-grained topic for precise retrieval and scoring.
    """

    id: str = Field(
        ...,
        description="Unique identifier. Format: <topic>_<sequence>, e.g. 'leave_casual_001'",
    )
    topic: str = Field(
        ...,
        description="Fine-grained topic tag that maps to a single, clear question.",
    )
    keywords: list[str] = Field(
        ...,
        description="Natural language keywords/phrases a user might search for. Must be non-empty.",
    )
    question: str = Field(
        ...,
        description="The canonical question this fact answers.",
    )
    answer: str = Field(
        ...,
        description="The grounded, complete-sentence answer safe for an LLM.",
    )
    weight: float = Field(
        default=1.0,
        description="Importance multiplier for relevance scoring. Default: 1.0",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """
        Validate id format: <topic>_<sequence>.
        Pattern: lowercase letters/underscores + underscore + 3-digit sequence.
        Example: leave_casual_001, it_laptop_002
        """
        pattern = r"^[a-z_]+_\d{3}$"
        if not re.match(pattern, v):
            raise ValueError(
                f"ID must match pattern '{pattern}'. Got: {v}"
            )
        return v

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """
        Validate topic is non-empty, lowercase, and snake_case.
        """
        if not v or not v.strip():
            raise ValueError("topic must be a non-empty string")
        if not re.match(r"^[a-z_]+$", v):
            raise ValueError(
                f"topic must be lowercase snake_case. Got: {v}"
            )
        return v

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: list[str]) -> list[str]:
        """
        Validate keywords is a non-empty list of non-empty strings.
        """
        if not v:
            raise ValueError("keywords must be a non-empty list")
        for keyword in v:
            if not keyword or not keyword.strip():
                raise ValueError("Each keyword must be a non-empty string")
        return v

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """
        Validate question is non-empty.
        """
        if not v or not v.strip():
            raise ValueError("question must be a non-empty string")
        return v

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v: str) -> str:
        """
        Validate answer is non-empty.
        """
        if not v or not v.strip():
            raise ValueError("answer must be a non-empty string")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        """
        Validate weight is a non-negative float.
        Typically in range 0.5–2.0, but not strictly enforced.
        """
        if v < 0:
            raise ValueError(f"weight must be non-negative. Got: {v}")
        return v

    model_config = ConfigDict(str_strip_whitespace=True)


class ScoredMatch(BaseModel):
    """
    A knowledge entry paired with a relevance score.
    
    Used by Retriever to return ranked results.
    """
    entry: KnowledgeEntry = Field(..., description="The knowledge entry")
    score: float = Field(..., description="Relevance score (>= 0)")


class RetrievalResult(BaseModel):
    """
    Contract between the Retriever and the Conversation Core (P3).
    
    Encapsulates a complete retrieval result with confidence classification.
    The Conversation Core should be able to determine:
    - Did we find something? (check matches list)
    - What did we find? (check matches[0].entry)
    - How confident are we? (check confidence)
    
    Without ever needing to inspect raw scores.
    """
    query: str = Field(..., description="The original user query")
    matches: list[ScoredMatch] = Field(
        default_factory=list,
        description="Top N ranked matches (e.g. top 3). Empty if no matches found."
    )
    top_score: float = Field(
        default=0.0,
        description="Score of the top match, or 0 if no matches found."
    )
    confidence: Literal["strong", "weak", "none"] = Field(
        default="none",
        description="Confidence level based on top_score and thresholds."
    )
