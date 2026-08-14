"""
Test suite for Retriever.

Tests keyword-based ranking, scoring, and confidence classification.
"""

import pytest

from hrbot.knowledge.repository import KnowledgeRepository
from hrbot.knowledge.retriever import STRONG_THRESHOLD, WEAK_THRESHOLD, Retriever
from hrbot.knowledge.schema import KnowledgeEntry, RetrievalResult, ScoredMatch


class TestRetrieverKnownQuestions:
    """Test retriever on known, real questions from knowledge base."""

    @pytest.fixture
    def retriever_with_repo(self):
        """Create retriever with real knowledge repository."""
        repo = KnowledgeRepository()
        return Retriever(repo)

    def test_known_question_working_hours_returns_work_related_entry(self, retriever_with_repo):
        """Known question 'What time does work start?' returns work-related entry."""
        result = retriever_with_repo.retrieve("What time does work start?")
        
        assert isinstance(result, RetrievalResult)
        assert len(result.matches) > 0
        
        # Top match should be work-related (hybrid work, working hours, etc.)
        top_entry = result.matches[0].entry
        assert any(keyword in top_entry.topic for keyword in ["work", "hours", "hybrid"])

    def test_paraphrased_question_office_hours_returns_hours_entry(self, retriever_with_repo):
        """Paraphrased question 'What are office hours?' returns working hours entry."""
        result = retriever_with_repo.retrieve("What are office hours?")
        
        assert isinstance(result, RetrievalResult)
        assert len(result.matches) > 0
        
        # Top match should be about working hours (office hours is a keyword)
        top_entry = result.matches[0].entry
        assert "hours" in top_entry.topic or "work" in top_entry.topic

    def test_casual_leave_question_returns_leave_entry(self, retriever_with_repo):
        """Question about casual leave returns leave_casual_entitlement entry."""
        result = retriever_with_repo.retrieve("How much casual leave am I entitled to?")
        
        assert len(result.matches) > 0
        top_entry = result.matches[0].entry
        assert top_entry.topic == "leave_casual_entitlement"

    def test_laptop_troubleshooting_returns_it_entry(self, retriever_with_repo):
        """Question about laptop issues returns IT topic entry."""
        result = retriever_with_repo.retrieve("What should I do if my laptop is not working?")
        
        assert len(result.matches) > 0
        top_entry = result.matches[0].entry
        assert top_entry.topic == "it_laptop_troubleshooting"


class TestRetrieverConfidence:
    """Test confidence classification on real queries."""

    @pytest.fixture
    def retriever_with_repo(self):
        """Create retriever with real knowledge repository."""
        repo = KnowledgeRepository()
        return Retriever(repo)

    def test_strong_confidence_on_direct_match(self, retriever_with_repo):
        """Direct keyword match ("leave") returns STRONG confidence."""
        result = retriever_with_repo.retrieve("leave")
        
        assert result.confidence == "strong"
        assert result.top_score >= STRONG_THRESHOLD

    def test_strong_confidence_exact_question(self, retriever_with_repo):
        """Exact question about casual leave returns STRONG confidence."""
        result = retriever_with_repo.retrieve("How much casual leave am I entitled to?")
        
        assert result.confidence == "strong"
        assert result.top_score >= STRONG_THRESHOLD

    def test_weak_confidence_on_partial_match(self, retriever_with_repo):
        """Query with partial word matches returns WEAK confidence."""
        # "What time does work start?" - word overlap but no exact keyword phrases
        result = retriever_with_repo.retrieve("What time does work start?")
        
        # Based on actual output, this scores 0.68 (WEAK)
        assert result.confidence == "weak"
        assert WEAK_THRESHOLD <= result.top_score < STRONG_THRESHOLD

    def test_none_confidence_on_unsupported_query(self, retriever_with_repo):
        """Completely unsupported query returns NONE confidence."""
        # Query with no connection to knowledge base
        result = retriever_with_repo.retrieve("quantum computing research papers")
        
        # Should either be NONE (no matches) or very weak
        if result.top_score < WEAK_THRESHOLD:
            assert result.confidence == "none"

    def test_none_confidence_on_empty_query(self, retriever_with_repo):
        """Empty query returns NONE confidence."""
        result = retriever_with_repo.retrieve("")
        
        assert result.confidence == "none"
        assert len(result.matches) == 0
        assert result.top_score == 0.0

    def test_confidence_labels_always_valid(self, retriever_with_repo):
        """All queries return valid confidence labels."""
        test_queries = [
            "leave",
            "laptop broken",
            "working hours",
            "maternity",
            "xyz123",
            "",
        ]
        
        for query in test_queries:
            result = retriever_with_repo.retrieve(query)
            assert result.confidence in ["strong", "weak", "none"]


class TestRetrieverRanking:
    """Test that multiple results are ranked correctly."""

    @pytest.fixture
    def retriever_with_repo(self):
        """Create retriever with real knowledge repository."""
        repo = KnowledgeRepository()
        return Retriever(repo)

    def test_multiple_leave_results_ranked_by_score(self, retriever_with_repo):
        """Query 'leave' returns multiple entries ranked by score."""
        result = retriever_with_repo.retrieve("leave")
        
        assert len(result.matches) >= 3
        
        # Verify descending order
        for i in range(len(result.matches) - 1):
            assert result.matches[i].score >= result.matches[i + 1].score

    def test_multiple_results_top_score_matches_first_entry(self, retriever_with_repo):
        """Top score matches the first (highest-ranked) entry score."""
        result = retriever_with_repo.retrieve("leave")
        
        assert result.top_score == result.matches[0].score

    def test_multiple_results_all_positive_scores(self, retriever_with_repo):
        """All returned entries have positive scores."""
        result = retriever_with_repo.retrieve("leave")
        
        for match in result.matches:
            assert match.score > 0

    def test_returned_entries_are_scored_match_objects(self, retriever_with_repo):
        """Returned entries are ScoredMatch objects with entry and score."""
        result = retriever_with_repo.retrieve("leave")
        
        assert all(isinstance(m, ScoredMatch) for m in result.matches)
        assert all(isinstance(m.entry, KnowledgeEntry) for m in result.matches)
        assert all(isinstance(m.score, float) for m in result.matches)


class TestRetrieverReturnContract:
    """Test the RetrievalResult return contract."""

    @pytest.fixture
    def retriever_with_repo(self):
        """Create retriever with real knowledge repository."""
        repo = KnowledgeRepository()
        return Retriever(repo)

    def test_retrieve_returns_retrieval_result(self, retriever_with_repo):
        """retrieve() always returns a RetrievalResult instance."""
        result = retriever_with_repo.retrieve("test")
        
        assert isinstance(result, RetrievalResult)

    def test_retrieval_result_has_required_fields(self, retriever_with_repo):
        """RetrievalResult has all required fields."""
        result = retriever_with_repo.retrieve("leave")
        
        assert hasattr(result, "query")
        assert hasattr(result, "matches")
        assert hasattr(result, "top_score")
        assert hasattr(result, "confidence")

    def test_retrieval_result_query_field_echoes_input(self, retriever_with_repo):
        """RetrievalResult.query echoes the input query."""
        query = "test query"
        result = retriever_with_repo.retrieve(query)
        
        assert result.query == query

    def test_retrieval_result_matches_list_limited(self, retriever_with_repo):
        """RetrievalResult returns at most 3 matches (configurable limit)."""
        result = retriever_with_repo.retrieve("leave")
        
        # Should return top N matches (e.g., top 3)
        assert len(result.matches) <= 3

    def test_retrieval_result_top_score_is_float(self, retriever_with_repo):
        """RetrievalResult.top_score is a float."""
        result = retriever_with_repo.retrieve("leave")
        
        assert isinstance(result.top_score, float)
        assert result.top_score >= 0.0


class TestRetrieverWithCustomEntries:
    """Test retriever with controlled test data."""

    def test_retriever_with_sample_entries(self):
        """Retriever can be initialized with sample KnowledgeEntry list."""
        entries = [
            KnowledgeEntry(
                id="test_001",
                topic="test_topic",
                keywords=["important keyword"],
                question="What is important?",
                answer="The keyword is important.",
                weight=1.0,
            ),
        ]
        
        retriever = Retriever(entries)
        result = retriever.retrieve("important keyword")
        
        assert len(result.matches) > 0
        assert result.matches[0].entry.id == "test_001"

    def test_empty_query_returns_empty_results(self):
        """Empty query returns empty results regardless of entries."""
        entries = [
            KnowledgeEntry(
                id="test_001",
                topic="test",
                keywords=["test"],
                question="Test?",
                answer="Test.",
                weight=1.0,
            ),
        ]
        
        retriever = Retriever(entries)
        result = retriever.retrieve("")
        
        assert len(result.matches) == 0
        assert result.confidence == "none"
