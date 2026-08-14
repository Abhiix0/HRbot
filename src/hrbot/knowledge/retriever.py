"""
Knowledge Retrieval and Ranking

Implements keyword-based scoring and retrieval of knowledge entries.
No embeddings, no vector databases, no external API calls.
"""

import logging
import re

from hrbot.knowledge.repository import KnowledgeRepository
from hrbot.knowledge.schema import KnowledgeEntry, RetrievalResult, ScoredMatch

logger = logging.getLogger(__name__)

# Confidence classification thresholds
# Calibrated based on observed score ranges from real queries (Aug 2026):
#   - Strong match (exact phrase + weight): 5.26, 15.72
#   - Weak match (partial/generic overlap): 0.68, 0.79, 0.89
#   - None (no relevant content): < 0.5
# STRONG_THRESHOLD at 2.0 captures direct keyword matches (entry weight ~1.5 × exact match bonus)
# WEAK_THRESHOLD at 0.5 captures partial matches but filters generic word overlap noise
STRONG_THRESHOLD = 2.0
WEAK_THRESHOLD = 0.5



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

    def __init__(self, entries: list[KnowledgeEntry] | KnowledgeRepository):
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

    def retrieve(self, query: str) -> RetrievalResult:
        """
        Retrieve and rank knowledge entries matching the query.
        
        Returns a RetrievalResult containing:
        - matches: Top N ranked ScoredMatch objects (score > 0)
        - top_score: Score of the best match
        - confidence: "strong", "weak", or "none" based on top_score thresholds
        
        Args:
            query: User's natural language query
            
        Returns:
            RetrievalResult with confidence classification.
        """
        if not query or not query.strip():
            return RetrievalResult(
                query=query,
                matches=[],
                top_score=0.0,
                confidence="none"
            )

        query_normalized = query.lower().strip()
        all_matches = []

        for entry in self.entries:
            score = self._score_entry(query_normalized, entry)
            if score > 0:
                all_matches.append(ScoredMatch(entry=entry, score=score))

        # Sort by score descending
        all_matches.sort(key=lambda m: m.score, reverse=True)
        
        # Take top N matches (e.g. top 3)
        top_matches = all_matches[:3]
        top_score = top_matches[0].score if top_matches else 0.0
        confidence = self._classify_confidence(top_score)

        return RetrievalResult(
            query=query,
            matches=top_matches,
            top_score=top_score,
            confidence=confidence
        )

    def _classify_confidence(self, score: float) -> str:
        """
        Classify confidence level based on top match score.
        
        Args:
            score: Top match score
            
        Returns:
            "strong", "weak", or "none"
        """
        if score >= STRONG_THRESHOLD:
            return "strong"
        elif score >= WEAK_THRESHOLD:
            return "weak"
        else:
            return "none"


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

    def _exact_keyword_match(self, query: str, keywords: list[str]) -> float:
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

    def _partial_keyword_match(self, query: str, keywords: list[str]) -> float:
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
    def _tokenize(text: str) -> list[str]:
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
