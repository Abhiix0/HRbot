import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    def __init__(self):
        self.knowledge_dir = Path(__file__).parent.parent.parent.parent / "knowledge"
        self.data = {}

    def load(self) -> None:
        if not self.knowledge_dir.exists():
            return

        for filepath in self.knowledge_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.data[filepath.stem] = json.load(f)
            except (OSError, json.JSONDecodeError):
                logger.exception("Failed to load knowledge file %s", filepath)

    def search(self, query: str) -> str:
        # A simple keyword matcher for now
        results = []
        query_lower = query.lower()
        for category, content in self.data.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    if query_lower in key.lower() or query_lower in str(value).lower():
                        results.append(f"[{category}] {key}: {value}")
        return "\n".join(results)
