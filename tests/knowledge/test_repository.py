"""
Tests for KnowledgeRepository.

Tests the loading, parsing, and validation of knowledge base entries.
"""

import json
import logging
import tempfile
from pathlib import Path

import pytest

from src.hrbot.knowledge.repository import KnowledgeRepository
from src.hrbot.knowledge.schema import KnowledgeEntry


@pytest.fixture
def temp_kb_dir():
    """Create a temporary directory for test knowledge files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def fixtures_dir():
    """Get the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestKnowledgeRepository:
    """Test suite for KnowledgeRepository."""

    def test_load_valid_files(self, temp_kb_dir):
        """Test loading valid knowledge base files."""
        # Create a valid test file
        test_data = [
            {
                "id": "test_entry_001",
                "topic": "test_topic",
                "keywords": ["test", "keyword"],
                "question": "What is this?",
                "answer": "This is a test entry.",
                "weight": 1.0,
            },
            {
                "id": "test_entry_002",
                "topic": "test_topic",
                "keywords": ["another", "test"],
                "question": "Another question?",
                "answer": "Another test answer.",
                "weight": 1.5,
            },
        ]
        
        test_file = temp_kb_dir / "test.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        entries = repo.load()

        assert len(entries) == 2
        assert all(isinstance(e, KnowledgeEntry) for e in entries)
        assert entries[0].id == "test_entry_001"
        assert entries[1].id == "test_entry_002"

    def test_load_multiple_files(self, temp_kb_dir):
        """Test loading multiple knowledge base files."""
        # Create two test files
        file1_data = [
            {
                "id": "topic_one_001",
                "topic": "topic_one",
                "keywords": ["kw1"],
                "question": "Q1?",
                "answer": "A1.",
            }
        ]
        file2_data = [
            {
                "id": "topic_two_001",
                "topic": "topic_two",
                "keywords": ["kw2"],
                "question": "Q2?",
                "answer": "A2.",
            }
        ]

        with open(temp_kb_dir / "file1.json", "w", encoding="utf-8") as f:
            json.dump(file1_data, f)
        with open(temp_kb_dir / "file2.json", "w", encoding="utf-8") as f:
            json.dump(file2_data, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        entries = repo.load()

        assert len(entries) == 2
        ids = {e.id for e in entries}
        assert "topic_one_001" in ids
        assert "topic_two_001" in ids

    def test_load_with_broken_json_file(self, temp_kb_dir, caplog):
        """Test that broken JSON files are skipped with a warning."""
        # Create a valid file and a broken file
        valid_data = [
            {
                "id": "valid_001",
                "topic": "valid_topic",
                "keywords": ["kw"],
                "question": "Q?",
                "answer": "A.",
            }
        ]
        
        with open(temp_kb_dir / "valid.json", "w", encoding="utf-8") as f:
            json.dump(valid_data, f)
        
        with open(temp_kb_dir / "broken.json", "w") as f:
            f.write("{ invalid json }")

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        # Should load the valid entry and skip the broken file
        assert len(entries) == 1
        
        # Check that a warning was logged for the broken file
        assert any("broken.json" in record.message for record in caplog.records)

    def test_load_with_invalid_schema_entries(self, temp_kb_dir, caplog):
        """Test that entries failing schema validation are skipped."""
        # Create a file with mixed valid and invalid entries
        mixed_data = [
            {
                "id": "valid_001",
                "topic": "topic_valid",
                "keywords": ["kw"],
                "question": "Q?",
                "answer": "A.",
            },
            {
                "id": "INVALID_ID_FORMAT",  # Invalid ID format
                "topic": "topic_invalid",
                "keywords": ["kw"],
                "question": "Q?",
                "answer": "A.",
            },
            {
                "id": "valid_002",
                "topic": "topic_other",
                "keywords": ["kw"],
                "question": "Q?",
                "answer": "A.",
            },
        ]
        
        with open(temp_kb_dir / "mixed.json", "w", encoding="utf-8") as f:
            json.dump(mixed_data, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        # Should load the 2 valid entries and skip the invalid one
        assert len(entries) == 2
        ids = {e.id for e in entries}
        assert "valid_001" in ids
        assert "valid_002" in ids
        assert "INVALID_ID_FORMAT" not in ids
        
        # Check that a warning was logged for the invalid entry
        assert any("INVALID_ID_FORMAT" in record.message for record in caplog.records)

    def test_load_empty_directory(self, temp_kb_dir, caplog):
        """Test loading from an empty directory."""
        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        assert len(entries) == 0
        assert any("No JSON files found" in record.message for record in caplog.records)

    def test_load_nonexistent_directory(self, caplog):
        """Test loading from a nonexistent directory."""
        repo = KnowledgeRepository(knowledge_dir=Path("/nonexistent/path"))
        
        with caplog.at_level(logging.ERROR):
            entries = repo.load()

        assert len(entries) == 0
        assert any("does not exist" in record.message for record in caplog.records)

    def test_load_non_array_json_file(self, temp_kb_dir, caplog):
        """Test that JSON files not containing arrays are skipped."""
        # Create a file with a JSON object instead of array
        with open(temp_kb_dir / "object.json", "w", encoding="utf-8") as f:
            json.dump({"key": "value"}, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        assert len(entries) == 0
        assert any("Expected JSON array" in record.message for record in caplog.records)

    def test_load_summary_logging(self, temp_kb_dir, caplog):
        """Test that the summary is logged correctly."""
        # Create a valid file
        valid_data = [
            {
                "id": f"entry_{i:03d}",
                "topic": "topic",
                "keywords": ["kw"],
                "question": "Q?",
                "answer": "A.",
            }
            for i in range(3)
        ]
        
        with open(temp_kb_dir / "valid.json", "w", encoding="utf-8") as f:
            json.dump(valid_data, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        
        with caplog.at_level(logging.INFO):
            entries = repo.load()

        assert len(entries) == 3
        
        # Check summary log
        summary_logs = [r for r in caplog.records if "Loaded" in r.message and "entries from" in r.message]
        assert len(summary_logs) > 0
        assert "3 entries" in summary_logs[0].message
        assert "1 files" in summary_logs[0].message

    def test_load_fixture_broken_json(self, fixtures_dir, caplog):
        """Test loading the deliberately broken JSON fixture."""
        if not fixtures_dir.exists():
            pytest.skip("Fixtures directory not found")

        repo = KnowledgeRepository(knowledge_dir=fixtures_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        # The broken.json file should fail to parse
        # but invalid_schema.json should load 1 valid entry
        assert any("broken.json" in record.message for record in caplog.records)

    def test_load_fixture_invalid_schema(self, fixtures_dir, caplog):
        """Test loading the invalid schema fixture."""
        if not fixtures_dir.exists():
            pytest.skip("Fixtures directory not found")

        repo = KnowledgeRepository(knowledge_dir=fixtures_dir)
        
        with caplog.at_level(logging.WARNING):
            entries = repo.load()

        # invalid_schema.json should load 1 valid entry and skip 2 invalid ones
        invalid_entries = [e for e in entries if e.topic == "test_invalid" and e.id == "invalid_entry_001"]
        assert len(invalid_entries) == 1

    def test_repository_returns_knowledge_entry_objects(self, temp_kb_dir):
        """Test that the repository returns actual KnowledgeEntry objects."""
        test_data = [
            {
                "id": "test_001",
                "topic": "test",
                "keywords": ["k1", "k2"],
                "question": "Q?",
                "answer": "A.",
                "weight": 1.5,
            }
        ]
        
        with open(temp_kb_dir / "test.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        repo = KnowledgeRepository(knowledge_dir=temp_kb_dir)
        entries = repo.load()

        assert len(entries) == 1
        entry = entries[0]
        
        # Verify it's a KnowledgeEntry with all fields
        assert isinstance(entry, KnowledgeEntry)
        assert entry.id == "test_001"
        assert entry.topic == "test"
        assert entry.keywords == ["k1", "k2"]
        assert entry.question == "Q?"
        assert entry.answer == "A."
        assert entry.weight == 1.5
