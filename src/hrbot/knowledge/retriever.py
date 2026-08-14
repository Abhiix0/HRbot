"""
Knowledge Retrieval and Ranking

Implements keyword-based scoring and retrieval of knowledge entries.
No embeddings, no vector databases, no external API calls.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Union

from src.hrbot.knowledge.schema import KnowledgeEntry
from src.hrbot.knowledge.repository import KnowledgeRepository

logger = logging.getLogger(__name__)


@dataclass
class ScoredMatch:
    """A knowledge entry paired with a relevance score."""
    entry: KnowledgeEntry
    score: float


class Retriever:
    """
    Retrieves and ranks knowledge entries based on keyword matching.
    
    Scoring algorithm (keyword-based only):
    1. Exact keyword phrase match: Query contains or keyword contains query (highest weight, +3.0)
    2. Partial word overlap: Individual words from keywords overlap with query (medium weight, +1.5)
    3. Question word overlap: Words from query overlap with question (lower weight, +0.5)
    4. All raw scores are multiplied by entry.weight
    5. Return all entries with score > 0, sorted by score descending
    """

    def __init__(self, entries: Union[List[KnowledgeEntry], KnowledgeRepository]):
        """
        Initialize the retriever with knowledge entries.
        
        Args:
            entries: Either a list of KnowledgeEntry objects or a KnowledgeRepository instance.
                    If a repository, its load() method is called to get entries.
        """
        if isinstance(entries, KnowledgeRepository):
            self.entries = entries.load()
        else:
            self.entries = entries

    def retrieve(self, query: str) -> List[ScoredMatch]:
        """
        Retrieve and rank knowledge entries matching the query.
        
        Args:
            query: User's natural language query
            
        Returns:
            List of ScoredMatch objects sorted by score (descending).
            Only includes entries with score > 0.
        """
        if not query or not query.strip():
            return []

        query_normalized = query.lower().strip()
        results = []

        for entry in self.entries:
            score = self._score_entry(query_normalized, entry)
            if score > 0:
                results.append(ScoredMatch(entry=entry, score=score))

        # Sort by score descending
        results.sort(key=lambda m: m.score, reverse=True)
        return results

    def _score_entry(self, query: str, entry: KnowledgeEntry) -> float:
        """
        Compute relevance score for an entry against a query.
        
        Scoring:
        - Exact keyword phrase match: +3.0
        - Partial word overlap (keywords): +1.5
        - Question word overlap: +0.5
        - Multiply by entry.weight
        
        Args:
            query: Normalized (lowercase) query string
            entry: Knowledge entry to score
            
        Returns:
            Score >= 0
        """
        raw_score = 0.0

        # 1. Exact keyword phrase match (highest weight)
        raw_score += self._exact_keyword_match(query, entry.keywords) * 3.0

        # 2. Partial word overlap in keywords (medium weight)
        raw_score += self._partial_keyword_match(query, entry.keywords) * 1.5

        # 3. Question word overlap (lower weight)
        raw_score += self._question_overlap(query, entry.question) * 0.5

        # Multiply by entry weight
        final_score = raw_score * entry.weight
        return final_score

    def _exact_keyword_match(self, query: str, keywords: List[str]) -> float:
        """
        Check if any keyword (or phrase) appears in the query, or vice versa.
        Returns count of exact matches found (0 or more).
        """
        query_lower = query.lower()
        match_count = 0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check both directions: keyword in query or query in keyword
            if keyword_lower in query_lower or query_lower in keyword_lower:
                match_count += 1

        return float(match_count)

    def _partial_keyword_match(self, query: str, keywords: List[str]) -> float:
        """
        Measure partial word overlap between query and keywords.
        Scores based on how many query words appear in keyword phrases.
        Returns 0-1 score (normalized by number of keywords).
        """
        if not keywords:
            return 0.0

        query_words = self._tokenize(query)
        if not query_words:
            return 0.0

        total_overlap = 0.0

        for keyword in keywords:
            keyword_words = self._tokenize(keyword)
            if not keyword_words:
                continue

            # Count overlapping words
            overlap_count = sum(1 for qw in query_words if any(qw in kw or kw in qw for kw in keyword_words))
            overlap_ratio = overlap_count / max(len(query_words), len(keyword_words))
            total_overlap += overlap_ratio

        # Normalize by number of keywords
        return total_overlap / len(keywords) if keywords else 0.0

    def _question_overlap(self, query: str, question: str) -> float:
        """
        Measure word overlap between query and question.
        Returns 0-1 score based on ratio of overlapping words.
        """
        query_words = self._tokenize(query)
        question_words = self._tokenize(question)

        if not query_words or not question_words:
            return 0.0

        # Count overlapping words (substring match on normalized words)
        overlap_count = sum(1 for qw in query_words if any(qw in qw_q or qw_q in qw for qw_q in question_words))

        overlap_ratio = overlap_count / max(len(query_words), len(question_words))
        return overlap_ratio

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Tokenize text into lowercase words, removing punctuation.
        Returns list of words, filtered to non-empty strings.
        """
        # Remove punctuation and split on whitespace
        text = text.lower()
        # Keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w for w in words if w]
