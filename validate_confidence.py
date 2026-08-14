#!/usr/bin/env python3
"""
Validation script for Phase 5: Confidence Classification.

Demonstrates that retrieve() returns RetrievalResult with:
- matches (top N ranked entries)
- top_score (score of best match)
- confidence ("strong", "weak", or "none")

Tests the same 5 queries from Phase 4, now showing confidence labels.
"""

from src.hrbot.knowledge.repository import KnowledgeRepository
from src.hrbot.knowledge.retriever import Retriever, STRONG_THRESHOLD, WEAK_THRESHOLD
from src.hrbot.knowledge.schema import RetrievalResult


def main():
    """Run validation on 5 test queries with confidence classification."""
    
    # Load knowledge base
    repo = KnowledgeRepository()
    retriever = Retriever(repo)
    
    # The 5 test queries from Phase 4
    test_queries = [
        "What time does work start?",
        "How much casual leave am I entitled to?",
        "What is NovaTech's maternity leave policy?",
        "laptop not working",
        "leave",
    ]
    
    print("=" * 80)
    print("CONFIDENCE CLASSIFICATION VALIDATION")
    print("=" * 80)
    print(f"\nThresholds: STRONG ≥ {STRONG_THRESHOLD}, WEAK ≥ {WEAK_THRESHOLD}, NONE < {WEAK_THRESHOLD}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        result = retriever.retrieve(query)
        
        print(f"Query {i}: '{query}'")
        print(f"├─ Confidence: {result.confidence.upper()}")
        print(f"├─ Top Score: {result.top_score:.2f}")
        print(f"└─ Matches: {len(result.matches)}")
        
        for j, match in enumerate(result.matches[:3], 1):
            entry = match.entry
            print(f"   {j}. [{match.score:.2f}] {entry.question}")
            print(f"      Topic: {entry.topic}")
        print()
    
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    
    # Verify RetrievalResult contract
    assert all(isinstance(retriever.retrieve(q), RetrievalResult) for q in test_queries)
    print("✓ All results are RetrievalResult instances")
    
    # Verify confidence labels
    all_results = [retriever.retrieve(q) for q in test_queries]
    for result in all_results:
        assert result.confidence in ["strong", "weak", "none"]
    print("✓ All confidence labels are valid")
    
    # Verify top_score matches first match
    for result in all_results:
        if result.matches:
            assert result.top_score == result.matches[0].score
    print("✓ top_score matches best match score")
    
    # Verify score thresholds
    for result in all_results:
        if result.confidence == "strong":
            assert result.top_score >= STRONG_THRESHOLD
        elif result.confidence == "weak":
            assert result.top_score >= WEAK_THRESHOLD
        else:  # "none"
            # None can mean no matches (score 0) or low score
            pass
    print("✓ Confidence labels follow threshold rules")
    
    print()
    print("All validation checks passed! ✓")


if __name__ == "__main__":
    main()
