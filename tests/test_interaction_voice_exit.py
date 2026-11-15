import importlib
import os
import sys
import unittest
from unittest.mock import MagicMock

# sources.interaction imports sources.router, which loads heavy ML libraries
# (torch, transformers, adaptive_classifier) that are unrelated to the
# exit-phrase logic under test. Stub them only when they are not installed.
for _name in ("torch", "transformers", "adaptive_classifier"):
    try:
        importlib.import_module(_name)
    except ImportError:
        sys.modules[_name] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path
from sources.interaction import EXIT_PHRASES, Interaction


class FakeSpeechToText:
    """Speech2Text stand-in that replays scripted utterances instead of using a microphone.

    Once the script is exhausted it returns None a bounded number of times, then
    raises, so a listen loop that never terminates fails the test instead of
    hanging it (that is how the exit-phrase bug shows up).
    """
    EMPTY_POLL_LIMIT = 20

    def __init__(self, utterances):
        self.utterances = list(utterances)
        self.empty_polls = 0

    def get_result(self, echo_text, timeout=0.1):
        if not self.utterances:
            self.empty_polls += 1
            if self.empty_polls > self.EMPTY_POLL_LIMIT:
                raise RuntimeError("listen loop kept polling after the script ended")
            return None
        return {"text": self.utterances.pop(0)}


def make_interaction(utterances):
    """Build an Interaction without the hardware and model init done in __init__."""
    interaction = Interaction.__new__(Interaction)
    interaction.stt = FakeSpeechToText(utterances)
    interaction.speech = None
    interaction.ai_name = "jarvis"
    interaction.stt_enabled = True
    interaction.is_active = True
    interaction.last_query = None
    interaction.current_agent = None
    return interaction


class TestVoiceExitPhrase(unittest.TestCase):

    def test_exit_phrase_ends_listening(self):
        """Saying exactly an exit phrase must end the session (transcription_job -> None)."""
        interaction = make_interaction(["exit"])
        self.assertIsNone(interaction.transcription_job())

    def test_every_exit_phrase_ends_listening(self):
        for phrase in EXIT_PHRASES:
            with self.subTest(phrase=phrase):
                interaction = make_interaction([phrase])
                self.assertIsNone(interaction.transcription_job())

    def test_query_is_returned_with_transcription_marker(self):
        """A normal dictation still returns the query with the transcription marker."""
        interaction = make_interaction(["what is the weather in paris", "okay"])
        query = interaction.transcription_job()
        self.assertIsNotNone(query)
        self.assertIn("what is the weather in paris", query)
        self.assertIn("transcription", query)

    def test_sentence_containing_exit_word_is_not_an_exit(self):
        """Only an exact utterance match ends the session; a sentence containing the word does not."""
        interaction = make_interaction(["when does the show exit the catalog", "okay"])
        query = interaction.transcription_job()
        self.assertIsNotNone(query)

    def test_get_user_ends_session_on_exit_phrase(self):
        """get_user must stop the session instead of failing on the None transcript."""
        interaction = make_interaction(["goodbye"])
        self.assertIsNone(interaction.get_user())
        self.assertFalse(interaction.is_active)
        self.assertIsNone(interaction.last_query)

    def test_get_user_prefixes_normal_transcription(self):
        interaction = make_interaction(["hello jarvis", "that's all"])
        query = interaction.get_user()
        self.assertTrue(query.startswith("TTS transcription of user: "))
        self.assertIn("hello jarvis", query)
        self.assertTrue(interaction.is_active)


if __name__ == "__main__":
    unittest.main()
