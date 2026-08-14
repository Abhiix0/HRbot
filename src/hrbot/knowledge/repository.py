"""
Knowledge Repository

Handles loading and management of all knowledge base entries from JSON files.
Validates each entry against the KnowledgeEntry schema and provides a unified
interface for accessing all knowledge facts.
"""

import json
import logging
from pathlib import Path
from typing import List

from src.hrbot.knowledge.schema import KnowledgeEntry

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """
    Loads and manages knowledge base entries from JSON files.
    
    Design Decisions:
    - Skip strategy: Per-entry. If an entry fails schema validation, log a warning,
      skip that entry, and continue loading from the same file. This allows partial
      loading when a file has mostly valid entries with a few malformed ones.
    - If an entire file fails to parse as JSON, log an error and skip the whole file,
      then continue with the next file.
    - The load() method is fault-tolerant: it never raises an exception. Even if all
      files are broken, it returns an empty list and logs the failures.
    """

    def __init__(self, knowledge_dir: Path = None):
        """
        Initialize the repository.
        
        Args:
            knowledge_dir: Path to the directory containing knowledge JSON files.
                          If None, defaults to <repo_root>/knowledge/
        """
        if knowledge_dir is None:
            # Calculate relative to this file: src/hrbot/knowledge/repository.py
            # Up 4 levels to repo root, then into knowledge/
            self.knowledge_dir = Path(__file__).parent.parent.parent.parent / "knowledge"
        else:
            self.knowledge_dir = knowledge_dir

    def load(self) -> List[KnowledgeEntry]:
        """
        Load all knowledge entries from JSON files in the knowledge directory.
        
        Returns:
            A flat list of all valid KnowledgeEntry objects from all files,
            merged together. If no files are found or all files fail, returns
            an empty list.
            
        Logging:
            - Logs one summary line: "Loaded N entries from M files, K failures"
            - For each file failure (JSON parse error), logs a warning
            - For each entry failure (schema validation error), logs a warning
        """
        if not self.knowledge_dir.exists():
            logger.error("Knowledge directory does not exist: %s", self.knowledge_dir)
            return []

        all_entries: List[KnowledgeEntry] = []
        files_processed = 0
        files_failed = 0
        entries_failed = 0

        json_files = sorted(self.knowledge_dir.glob("*.json"))

        if not json_files:
            logger.warning("No JSON files found in knowledge directory: %s", self.knowledge_dir)
            return []

        for filepath in json_files:
            files_processed += 1
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                files_failed += 1
                logger.warning(
                    "Failed to parse JSON in %s: %s", filepath.name, str(e)
                )
                continue
            except OSError as e:
                files_failed += 1
                logger.warning(
                    "Failed to read file %s: %s", filepath.name, str(e)
                )
                continue

            # Expect a JSON array at the top level
            if not isinstance(data, list):
                files_failed += 1
                logger.warning(
                    "Expected JSON array in %s, got %s", filepath.name, type(data).__name__
                )
                continue

            # Process each entry in the file
            for idx, entry_data in enumerate(data):
                try:
                    entry = KnowledgeEntry(**entry_data)
                    all_entries.append(entry)
                except Exception as e:
                    entries_failed += 1
                    entry_id = entry_data.get("id", f"(unknown at index {idx})")
                    logger.warning(
                        "Failed to validate entry %s in %s: %s",
                        entry_id,
                        filepath.name,
                        str(e),
                    )
                    continue

        # Log summary
        total_files = len(json_files)
        total_failures = files_failed + entries_failed
        logger.info(
            "Loaded %d entries from %d files, %d failures",
            len(all_entries),
            total_files,
            total_failures,
        )

        return all_entries
