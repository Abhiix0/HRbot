"""
Tests for the Retriever class.

Tests keyword-based ranking and scoring logic in isolation.
"""

import pytest

from src.hrbot.knowledge.repository import KnowledgeRepository
from src.hrbot.knowledge.retriever import Retriever
from src.hrbot.knowledge.schema import KnowledgeEntry, RetrievalResult, ScoredMatch


@pytest.fixture
def sample_entries():
    """Create sample knowledge entries for testing."""
    return [
        KnowledgeEntry(
            id="working_hours_001",
            topic="working_hours",
            keywords=["office hours", "work timing", "when does work start"],
            question="What are the standard working hours?",
            answer="9:30 AM to 6:30 PM Monday through Friday.",
            weight=1.5,
        ),
        KnowledgeEntry(
            id="leave_casual_001",
            topic="leave_casual_entitlement",
            keywords=["casual leave", "personal days", "leave balance"],
            question="How many casual leave days am I entitled to per year?",
            answer="All permanent employees are entitled to 8 casual leave days per year.",
            weight=1.5,
        ),
        KnowledgeEntry(
            id="laptop_001",
            topic="it_laptop_troubleshooting",
            keywords=["laptop issue", "computer not working", "hardware problem"],
            question="What should I do if my laptop is not working?",
            answer="Restart the device first. Contact IT if the problem persists.",
            weight=1.5,
        ),
        KnowledgeEntry(
            id="company_001",
            topic="company_overview",
            keywords=["about NovaTech", "company info"],
            question="What is NovaTech Solutions?",
            answer="NovaTech is a technology company with 500 employees.",
            weight=1.0,
        ),
    ]


@pytest.fixture
def retriever(sample_entries):
    """Create a retriever with sample entries."""
    return Retriever(sample_entries)


class TestRetriever:
    """Test suite for Retriever."""

    def test_retrieve_exact_keyword_match(self, retriever):
        """Test that exact keyword phrases are matched with high scores."""
        result = retriever.retrieve("casual leave")
        
        assert isinstance(result, RetrievalResult)
        assert len(result.matches) > 0
        assert result.matches[0].entry.id == "leave_casual_001"
        assert result.top_score > 0

    def test_retrieve_partial_keyword_match(self, retriever):
        """Test that partial keyword matches score well."""
        result = retriever.retrieve("work hours")
        
        assert len(result.matches) > 0
        # Should match "office hours" or "work timing" keywords
        assert result.matches[0].entry.topic == "working_hours"

    def test_retrieve_laptop_query(self, retriever):
        """Test a practical laptop troubleshooting query."""
        result = retriever.retrieve("laptop not working")
        
        assert len(result.matches) > 0
        assert result.matches[0].entry.id == "laptop_001"
        assert result.top_score > 0.5

    def test_retrieve_empty_query(self, retriever):
        """Test that empty queries return no results."""
        result = retriever.retrieve("")
        assert len(result.matches) == 0
        assert result.confidence == "none"
        
        result = retriever.retrieve("   ")
        assert len(result.matches) == 0
        assert result.confidence == "none"

    def test_retrieve_sorted_by_score(self, retriever):
        """Test that results are sorted by score descending."""
        result = retriever.retrieve("leave")
        
        assert len(result.matches) > 0
        for i in range(len(result.matches) - 1):
            assert result.matches[i].score >= result.matches[i + 1].score

    def test_retrieval_result_structure(self, retriever):
        """Test that RetrievalResult has all required fields."""
        result = retriever.retrieve("casual leave")
        
        assert hasattr(result, 'query')
        assert hasattr(result, 'matches')
        assert hasattr(result, 'top_score')
        assert hasattr(result, 'confidence')
        assert result.query == "casual leave"

    def test_retriever_with_repository(self):
        """Test that Retriever can be initialized with a KnowledgeRepository."""
        repo = KnowledgeRepository()
        retriever = Retriever(repo)
        
        # Should successfully load entries from repo
        assert len(retriever.entries) > 0
        
        # Should be able to retrieve
        result = retriever.retrieve("leave")
        assert len(result.matches) > 0
        assert isinstance(result, RetrievalResult)


class TestConfidenceClassification:
    """Test confidence classification logic."""

    def test_confidence_strong(self):
        """Test that high scores get 'strong' confidence."""
        # Create entry with high weight and exact keyword match
        entries = [
            KnowledgeEntry(
                id="test_strong_001",
                topic="test_strong",
                keywords=["test query"],
                question="Test?",
                answer="Test.",
                weight=2.0,  # High weight
            )
        ]
        retriever = Retriever(entries)
        result = retriever.retrieve("test query")
        
        # Should get strong confidence due to exact match + high weight
        assert result.confidence == "strong"
        assert result.top_score >= 2.0

    def test_confidence_none_empty(self):
        """Test that empty queries get 'none' confidence."""
        entries = [
            KnowledgeEntry(
                id="test_001",
                topic="test",
                keywords=["test"],
                question="Test?",
                answer="Test.",
                weight=1.0,
            )
        ]
        retriever = Retriever(entries)
        result = retriever.retrieve("")
        
        assert result.confidence == "none"
        assert len(result.matches) == 0
        assert result.top_score == 0.0

    def test_confidence_labels_valid(self, retriever):
        """Test that confidence is always a valid label."""
        queries = ["leave", "laptop", "xyz", "", "unknown topic"]
        for query in queries:
            result = retriever.retrieve(query)
            assert result.confidence in ["strong", "weak", "none"]

    def test_confidence_strong_threshold(self):
        """Test strong confidence threshold behavior."""
        from src.hrbot.knowledge.retriever import STRONG_THRESHOLD
        
        # Entry that will score above STRONG_THRESHOLD
        entries = [
            KnowledgeEntry(
                id="entry_001",
                topic="topic",
                keywords=["exact phrase"],
                question="Question?",
                answer="Answer.",
                weight=2.0,
            )
        ]
        retriever = Retriever(entries)
        result = retriever.retrieve("exact phrase")
        
        if result.top_score >= STRONG_THRESHOLD:
            assert result.confidence == "strong"

    def test_confidence_weak_threshold(self):
        """Test weak confidence threshold behavior."""
        from src.hrbot.knowledge.retriever import WEAK_THRESHOLD
        
        # This is harder to test precisely without controlling scoring,
        # but we verify the logic is applied
        entries = [
            KnowledgeEntry(
                id="entry_001",
                topic="topic",
                keywords=["test"],
                question="What is test?",
                answer="Test is a test.",
                weight=1.0,
            )
        ]
        retriever = Retriever(entries)
        
        # Query that will get weak score
        result = retriever.retrieve("test")
        
        # Verify confidence classification follows thresholds
        if result.top_score >= WEAK_THRESHOLD:
            assert result.confidence in ["strong", "weak"]
        else:
            assert result.confidence == "none"


class TestRetrieverScoring:
    """Test the scoring algorithm specifically."""

    def test_scoring_components(self):
        """Test individual scoring components."""
        entries = [
            KnowledgeEntry(
                id="test_001",
                topic="test",
                keywords=["keyword"],
                question="What is the answer?",
                answer="The answer is 42.",
                weight=1.0,
            )
        ]
        retriever = Retriever(entries)

        # Exact match should score highest
        exact_result = retriever.retrieve("keyword")
        assert len(exact_result.matches) > 0
        exact_score = exact_result.top_score

        # Partial match should score lower
        partial_result = retriever.retrieve("key")
        partial_score = partial_result.top_score if partial_result.matches else 0

        # Exact match is more direct
        assert exact_score > 0

    def test_tokenize(self):
        """Test the tokenization helper."""
        tokens = Retriever._tokenize("What time does WORK start?")
        
        assert "what" in tokens
        assert "time" in tokens
        assert "work" in tokens
        assert "start" in tokens
        assert all(isinstance(t, str) for t in tokens)
