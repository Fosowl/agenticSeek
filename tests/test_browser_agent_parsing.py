import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path

# Mock heavy dependencies
for mod_name in [
    'torch', 'transformers', 'kokoro', 'adaptive_classifier', 'text2emotion',
    'ollama', 'openai', 'together', 'IPython', 'IPython.display',
    'playsound3', 'soundfile', 'pyaudio', 'librosa',
    'pypdf', 'langid', 'pypinyin', 'fake_useragent',
    'chromedriver_autoinstaller', 'num2words', 'sentencepiece', 'sacremoses',
    'scipy', 'numpy', 'selenium_stealth', 'undetected_chromedriver',
    'markdownify',
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

os.environ.setdefault('WORK_DIR', '/tmp')

from sources.agents.browser_agent import BrowserAgent

class TestBrowserAgentParsing(unittest.TestCase):
    def setUp(self):
        self.agent = BrowserAgent.__new__(BrowserAgent)
        self.agent.notes = []
        self.agent.navigable_links = []
        self.agent.search_history = []
        self.agent.current_page = ""
        self.agent.logger = MagicMock()

    def test_extract_links(self):
        test_text = """
        Check this out: https://thriveonai.com/15-ai-startups-in-japan-to-take-note-of, and www.google.com!
        Also try https://test.org/about?page=1, hey this one as well bro https://weatherstack.com/documentation/.
        """
        expected = [
            "https://thriveonai.com/15-ai-startups-in-japan-to-take-note-of",
            "www.google.com",
            "https://test.org/about?page=1",
            "https://weatherstack.com/documentation"
        ]
        result = self.agent.extract_links(test_text)
        self.assertEqual(result, expected)

    def test_extract_links_no_links(self):
        """Test that text without links returns empty list."""
        result = self.agent.extract_links("No links here at all.")
        self.assertEqual(result, [])

    def test_extract_links_single_link(self):
        """Test extraction of a single link."""
        result = self.agent.extract_links("Visit https://example.com for details")
        self.assertEqual(result, ["https://example.com"])

    def test_extract_form(self):
        test_text = """
        Fill this: [username](john) and [password](secret123)
        Not a form: [random]text
        """
        expected = ["[username](john)", "[password](secret123)"]
        result = self.agent.extract_form(test_text)
        self.assertEqual(result, expected)

    def test_extract_form_empty(self):
        """Test form extraction with no form inputs."""
        result = self.agent.extract_form("Just regular text here.")
        self.assertEqual(result, [])

    def test_extract_form_checkbox(self):
        """Test form extraction with checkbox values."""
        text = "[agree](checked) and [newsletter](unchecked)"
        result = self.agent.extract_form(text)
        self.assertEqual(len(result), 2)

    def test_clean_links(self):
        test_links = [
            "https://example.com.",
            "www.test.com,",
            "https://clean.org!",
            "https://good.com"
        ]
        expected = [
            "https://example.com",
            "www.test.com",
            "https://clean.org",
            "https://good.com"
        ]
        result = self.agent.clean_links(test_links)
        self.assertEqual(result, expected)

    def test_clean_links_with_slash(self):
        """Test that trailing slash is stripped since it's not alphanumeric."""
        links = ["https://example.com/path/"]
        result = self.agent.clean_links(links)
        self.assertEqual(result, ["https://example.com/path"])

    def test_parse_answer(self):
        test_text = """
        Here's some info
        Note: This is important. We are doing test it's very cool.
        action: 
        i wanna navigate to https://test.com
        """
        self.agent.parse_answer(test_text)
        self.assertEqual(self.agent.notes[0], "Note: This is important. We are doing test it's very cool.")

    def test_parse_answer_extracts_links(self):
        """Test that parse_answer returns extracted links."""
        text = "Navigate to https://example.com and https://test.org"
        links = self.agent.parse_answer(text)
        self.assertIn("https://example.com", links)
        self.assertIn("https://test.org", links)

    def test_parse_answer_no_notes(self):
        """Test parse_answer with no notes section."""
        text = "Go to https://example.com"
        self.agent.parse_answer(text)
        # Notes should have an empty entry
        self.assertEqual(len(self.agent.notes), 1)

    def test_select_link_unvisited(self):
        """Test selecting first unvisited link."""
        self.agent.search_history = ["https://visited.com"]
        self.agent.current_page = "https://current.com"
        links = ["https://visited.com", "https://current.com", "https://new.com"]
        result = self.agent.select_link(links)
        self.assertEqual(result, "https://new.com")

    def test_select_link_all_visited(self):
        """Test that None is returned when all links are visited."""
        self.agent.search_history = ["https://a.com", "https://b.com"]
        self.agent.current_page = ""
        links = ["https://a.com", "https://b.com"]
        result = self.agent.select_link(links)
        self.assertIsNone(result)

    def test_select_link_empty(self):
        """Test with empty links list."""
        result = self.agent.select_link([])
        self.assertIsNone(result)

    def test_jsonify_search_results(self):
        """Test parsing search result text into structured data."""
        text = """Title: Result One
Snippet: First result snippet
Link: https://one.com

Title: Result Two
Snippet: Second result snippet
Link: https://two.com"""
        results = self.agent.jsonify_search_results(text)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Result One")
        self.assertEqual(results[0]["link"], "https://one.com")
        self.assertEqual(results[1]["snippet"], "Second result snippet")

    def test_jsonify_search_results_empty(self):
        """Test with empty search results."""
        results = self.agent.jsonify_search_results("")
        self.assertEqual(results, [])

    def test_jsonify_search_results_partial(self):
        """Test with partial result (only title and link)."""
        text = """Title: Partial Result
Link: https://partial.com"""
        results = self.agent.jsonify_search_results(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Partial Result")
        self.assertNotIn("snippet", results[0])

    def test_stringify_search_results(self):
        """Test converting structured results back to string."""
        results = [
            {"link": "https://one.com", "snippet": "First snippet"},
            {"link": "https://two.com", "snippet": "Second snippet"}
        ]
        output = self.agent.stringify_search_results(results)
        self.assertIn("https://one.com", output)
        self.assertIn("First snippet", output)
        self.assertIn("https://two.com", output)

    def test_select_unvisited(self):
        """Test filtering visited results."""
        self.agent.search_history = ["https://visited.com"]
        results = [
            {"link": "https://visited.com", "title": "Old"},
            {"link": "https://new.com", "title": "New"}
        ]
        unvisited = self.agent.select_unvisited(results)
        self.assertEqual(len(unvisited), 1)
        self.assertEqual(unvisited[0]["link"], "https://new.com")

    def test_select_unvisited_all_new(self):
        """Test when no results are visited."""
        self.agent.search_history = []
        results = [
            {"link": "https://a.com", "title": "A"},
            {"link": "https://b.com", "title": "B"}
        ]
        unvisited = self.agent.select_unvisited(results)
        self.assertEqual(len(unvisited), 2)


if __name__ == "__main__":
    unittest.main()