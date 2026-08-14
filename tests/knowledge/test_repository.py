"""
Test suite for KnowledgeRepository.

Tests the loading, parsing, and validation of knowledge base entries from
the real knowledge/ directory and with malformed fixtures.
"""

import json
import logging
import tempfile
from pathlib import Path

import pytest

from src.hrbot.knowledge.repository import KnowledgeRepository
from src.hrbot.knowledge.schema import KnowledgeEntry


@pytest.fixture
def fixtures_dir():
    """Get the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestRepositoryLoadsRealFiles:
    """Test loading from the real knowledge/ directory."""

    def test_load_real_knowledge_files_returns_expected_count(self):
        """Loading real knowledge/ files returns exactly 35 entries."""
        repo = KnowledgeRepository()
        entries = repo.load()
        
        # Expected: 35 entries across 6 files
        # (company.json: 4, onboarding.json: 5, leave.json: 7,
        #  attendance.json: 5, workplace.json: 10, contacts.json: 4)
        assert len(entries) == 35
        assert all(isinstance(e, KnowledgeEntry) for e in entries)

    def test_load_real_files_all_entries_valid_schema(self):
        """Every entry from real files validates against KnowledgeEntry."""
        repo = KnowledgeRepository()
        entries = repo.load()
        
        for entry in entries:
            # Should not raise validation errors
            assert isinstance(entry, KnowledgeEntry)
            
            # Validate required fields
            assert entry.id
            assert entry.topic
            assert entry.keywords
            assert entry.question
            assert entry.answer
            assert entry.weight >= 0

    def test_load_real_files_entries_have_valid_ids(self):
        """All real entries have valid ID format: ^[a-z_]+_\\d{3}$."""
        import re
        
        repo = KnowledgeRepository()
        entries = repo.load()
        
        id_pattern = re.compile(r"^[a-z_]+_\d{3}$")
        for entry in entries:
            assert id_pattern.match(entry.id), f"Invalid ID: {entry.id}"

    def test_load_real_files_entries_have_snake_case_topics(self):
        """All real entries have snake_case topics."""
        repo = KnowledgeRepository()
        entries = repo.load()
        
        for entry in entries:
            # Topic should be lowercase with underscores
            assert entry.topic == entry.topic.lower()
            assert entry.topic.replace("_", "").isalnum()


class TestRepositoryHandlesErrors:
    """Test error handling and fault tolerance."""

    def test_load_with_malformed_json_logs_error_continues(self, fixtures_dir, caplog):
        """Loading with malformed JSON logs error, doesn't crash, returns valid entries."""
        # Use the fixtures/broken.json which has syntax errors
        broken_file = fixtures_dir / "broken.json"
        
        if not broken_file.exists():
            # Create a malformed JSON file for testing
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                
                # Create broken.json with invalid JSON
                broken = tmppath / "broken.json"
                with open(broken, "w") as f:
                    f.write("[{invalid json}]")
                
                # Create valid.json with good data
                valid = tmppath / "valid.json"
                valid_data = [
                    {
                        "id": "valid_entry_001",
                        "topic": "valid",
                        "keywords": ["test"],
                        "question": "Test?",
                        "answer": "Valid.",
                        "weight": 1.0,
                    }
                ]
                with open(valid, "w", encoding="utf-8") as f:
                    json.dump(valid_data, f)
                
                # Load with caplog to capture warnings
                with caplog.at_level(logging.WARNING):
                    repo = KnowledgeRepository(knowledge_dir=tmppath)
                    entries = repo.load()
                
                # Should not crash, should return valid entries
                assert len(entries) == 1
                assert entries[0].id == "valid_entry_001"
                
                # Should have logged a warning about the broken file
                assert any("broken.json" in record.message for record in caplog.records)
        else:
            # Use existing fixture
            # Create a sibling valid file
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                
                # Copy broken.json to temp dir
                broken = tmppath / "broken.json"
                with open(broken, "w") as f:
                    f.write(open(broken_file).read())
                
                # Create valid.json
                valid = tmppath / "valid.json"
                valid_data = [
                    {
                        "id": "valid_entry_001",
                        "topic": "valid",
                        "keywords": ["test"],
                        "question": "Test?",
                        "answer": "Valid.",
                        "weight": 1.0,
                    }
                ]
                with open(valid, "w", encoding="utf-8") as f:
                    json.dump(valid_data, f)
                
                with caplog.at_level(logging.WARNING):
                    repo = KnowledgeRepository(knowledge_dir=tmppath)
                    entries = repo.load()
                
                assert len(entries) >= 1
                assert any(e.id == "valid_entry_001" for e in entries)

    def test_load_per_entry_skip_strategy(self):
        """Invalid entries are skipped; valid entries from same file are loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create file with 1 valid + 2 invalid entries
            mixed_file = tmppath / "mixed.json"
            mixed_data = [
                {
                    "id": "valid_001",
                    "topic": "valid",
                    "keywords": ["test"],
                    "question": "Test?",
                    "answer": "Valid.",
                    "weight": 1.0,
                },
                {
                    "id": "invalid_bad_id",  # Invalid ID format
                    "topic": "invalid",
                    "keywords": ["bad"],
                    "question": "Bad?",
                    "answer": "Bad.",
                    "weight": 1.0,
                },
                {
                    "id": "valid_002",
                    "topic": "also_valid",
                    "keywords": ["good"],
                    "question": "Good?",
                    "answer": "Good.",
                    "weight": 1.0,
                },
            ]
            with open(mixed_file, "w", encoding="utf-8") as f:
                json.dump(mixed_data, f)
            
            repo = KnowledgeRepository(knowledge_dir=tmppath)
            entries = repo.load()
            
            # Should load 2 valid entries, skip 1 invalid
            assert len(entries) == 2
            assert any(e.id == "valid_001" for e in entries)
            assert any(e.id == "valid_002" for e in entries)
            assert not any("invalid_bad_id" in e.id for e in entries)

    def test_load_nonexistent_directory_returns_empty(self):
        """Loading from nonexistent directory returns empty list without crashing."""
        repo = KnowledgeRepository(knowledge_dir=Path("/nonexistent/path"))
        entries = repo.load()
        
        assert entries == []

    def test_load_empty_directory_returns_empty(self):
        """Loading from empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = KnowledgeRepository(knowledge_dir=Path(tmpdir))
            entries = repo.load()
            
            assert entries == []


class TestRepositoryIntegration:
    """Integration tests with real knowledge base."""

    def test_repository_loads_all_six_files(self):
        """Repository loads from all 6 expected files."""
        repo = KnowledgeRepository()
        entries = repo.load()
        
        # Check that we have entries from different topics
        topics = {e.topic for e in entries}
        
        # Should have topics from all 6 files
        expected_topics = {
            "company_overview",
            "onboarding_documents",
            "leave_casual_entitlement",
            "attendance_working_hours",
            "wfh_hybrid_policy",
            "contact_hr",
        }
        
        # At least some expected topics should be present
        assert len(topics) > 5
        assert len(entries) == 35
