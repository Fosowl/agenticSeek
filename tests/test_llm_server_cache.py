import json
import os
import sys
import tempfile
import unittest

# llm_server ships its own "sources" package next to the repository root one.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'llm_server')))

from sources.cache import Cache

PAIR = {"user": "how do I sort a list?", "assistant": "call sorted()"}


class TestCache(unittest.TestCase):
    """The response cache must store, persist and reload user/assistant pairs."""

    def setUp(self):
        self._cache_dir = tempfile.TemporaryDirectory()
        self.cache_dir = self._cache_dir.name
        self.cache_file = os.path.join(self.cache_dir, "messages.json")

    def tearDown(self):
        self._cache_dir.cleanup()

    def test_stored_pair_is_not_a_set(self):
        """Regression: `set(json.load(...))` made add_message_pair and _save raise."""
        self.assertEqual(Cache(cache_dir=self.cache_dir).cache, [])

    def test_add_message_pair_persists_and_reloads(self):
        Cache(cache_dir=self.cache_dir).add_message_pair(PAIR["user"], PAIR["assistant"])
        with open(self.cache_file, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), [PAIR])
        reloaded = Cache(cache_dir=self.cache_dir)
        self.assertTrue(reloaded.is_cached(PAIR["user"]))
        self.assertEqual(reloaded.get_cached_response(PAIR["user"]), PAIR["assistant"])

    def test_existing_cache_file_is_loaded(self):
        """Regression: a non-empty cache file raised 'unhashable type: dict' at startup."""
        with open(self.cache_file, "w", encoding="utf-8") as handle:
            json.dump([PAIR], handle)
        self.assertEqual(Cache(cache_dir=self.cache_dir).get_cached_response(PAIR["user"]), PAIR["assistant"])

    def test_duplicate_user_message_is_ignored(self):
        cache = Cache(cache_dir=self.cache_dir)
        cache.add_message_pair(PAIR["user"], PAIR["assistant"])
        cache.add_message_pair(PAIR["user"], "second answer")
        self.assertEqual(len(cache.cache), 1)
        self.assertEqual(cache.get_cached_response(PAIR["user"]), PAIR["assistant"])

    def test_unknown_message_is_not_cached(self):
        cache = Cache(cache_dir=self.cache_dir)
        self.assertFalse(cache.is_cached("never asked"))
        self.assertIsNone(cache.get_cached_response("never asked"))


if __name__ == '__main__':
    unittest.main()
