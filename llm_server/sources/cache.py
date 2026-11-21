import os
import json
from pathlib import Path

class Cache:
    def __init__(self, cache_dir='.cache', cache_file='messages.json'):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / cache_file
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not self.cache_file.exists():
            with open(self.cache_file, 'w') as f:
                json.dump([], f)

        with open(self.cache_file, 'r') as f:
            self.cache = list(json.load(f))

    def add_message_pair(self, user_message: str, assistant_message: str):
        """Add a user/assistant pair to the cache if not present."""
        if not any(entry["user"] == user_message for entry in self.cache):
            self.cache.append({"user": user_message, "assistant": assistant_message})
            self._save()

    def is_cached(self, user_message: str) -> bool:
        """Check if a user msg is cached."""
        return any(entry["user"] == user_message for entry in self.cache)

    def get_cached_response(self, user_message: str) -> str | None:
        """Return the assistant response to a user message if cached."""
        for entry in self.cache:
            if entry["user"] == user_message:
                return entry["assistant"]
        return None

    def _save(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
