import unittest
from unittest.mock import MagicMock, patch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path
from sources.tools.searxSearch import searxSearch
from sources.errors import AgenticSeekError
from dotenv import load_dotenv
import requests  # Import the requests module

load_dotenv()

class TestSearxSearch(unittest.TestCase):

    def setUp(self):
        os.environ['SEARXNG_BASE_URL'] = "http://127.0.0.1:8080"  # Set the environment variable
        self.base_url = os.getenv("SEARXNG_BASE_URL")
        self.search_tool = searxSearch(base_url=self.base_url)
        self.valid_query = "test query"
        self.invalid_query = ""

    def test_initialization_with_env_variable(self):
        # Ensure the tool initializes correctly with the base URL from the environment variable
        os.environ['SEARXNG_BASE_URL'] = "http://test.example.com"
        search_tool = searxSearch()
        self.assertEqual(search_tool.base_url, "http://test.example.com")
        del os.environ['SEARXNG_BASE_URL']

    def test_initialization_no_base_url(self):
        # Ensure the tool raises an error if no base URL is provided
        # Remove the environment variable to ensure the configuration error is raised
        if 'SEARXNG_BASE_URL' in os.environ:
            del os.environ['SEARXNG_BASE_URL']
        with self.assertRaises(AgenticSeekError):
            searxSearch(base_url=None)
        # Restore the environment variable after the test
        os.environ['SEARXNG_BASE_URL'] = "http://searx.lan"

    def test_execute_valid_query(self):
        # Execute the search and verify the result
        result = self.search_tool.execute([self.valid_query])
        print(f"Output from test_execute_valid_query: {result}")
        self.assertTrue(isinstance(result, str), "Result should be a string.")
        self.assertNotEqual(result, "", "Result should not be empty. Check SearxNG instance.")

    def test_execute_empty_query(self):
        # Test with an empty query
        result = self.search_tool.execute([""])
        print(f"Output from test_execute_empty_query: {result}")
        self.assertEqual(result, "Error: Empty search query provided.")

    def test_execute_no_query(self):
        # Test with no query provided
        result = self.search_tool.execute([])
        print(f"Output from test_execute_no_query: {result}")
        self.assertEqual(result, "Error: No search query provided.")

    def test_execute_request_exception(self):
        # An unreachable SearxNG must raise, not return text the LLM would build on
        original_base_url = self.search_tool.base_url
        self.search_tool.base_url = "http://invalid_url"
        try:
            with self.assertRaises(AgenticSeekError) as ctx:
                self.search_tool.execute([self.valid_query])
            self.assertEqual(ctx.exception.title, "Web search unavailable")
        finally:
            self.search_tool.base_url = original_base_url  # Restore the original base_url

    def test_execute_no_results(self):
        # Execute the search and verify that an empty string is handled correctly
        result = self.search_tool.execute(["nonexistent query that should return no results"])
        print(f"Output from test_execute_no_results: {result}")
        self.assertTrue(isinstance(result, str), "Result should be a string.")
        # Allow empty results, but print a warning
        if result == "":
            print("Warning: SearxNG returned no results for a query that should have returned no results.")

    def test_execution_failure_check_error(self):
        # Test when the output contains an error
        output = "Error: Something went wrong"
        self.assertTrue(self.search_tool.execution_failure_check(output))

    def test_execution_failure_check_no_error(self):
        # Test when the output does not contain an error
        output = "Search completed successfully"
        self.assertFalse(self.search_tool.execution_failure_check(output))


def html_page(*links):
    articles = "".join(f'<article class="result"><a class="url_header" href="{link}"></a>'
                       f'<h3>{link}</h3><p class="content">snippet</p></article>' for link in links)
    return f"<html><body>{articles}</body></html>"


def http_response(status=200, text="", json_body=None, headers=None):
    response = MagicMock(status_code=status, text=text, headers=headers or {})
    response.json.return_value = json_body or {}
    response.raise_for_status.side_effect = requests.HTTPError(f"{status}") if status >= 400 else None
    return response


@patch('sources.tools.searxSearch.time.sleep')
@patch('sources.tools.searxSearch.pretty_print')
class TestSearxSearchFailures(unittest.TestCase):
    """SearxNG failures must surface as errors, never as an empty result the LLM fills with invented links."""

    def setUp(self):
        self.tool = searxSearch(base_url="http://127.0.0.1:8080")

    def test_connection_refused_raises_without_retry(self, _print, sleep):
        self.tool.base_url = "http://127.0.0.1:1"  # nothing listens there
        with self.assertRaises(AgenticSeekError) as ctx:
            self.tool.execute(["best antibes pizza"])
        self.assertEqual(ctx.exception.title, "Web search unavailable")
        sleep.assert_not_called()

    @patch('sources.tools.searxSearch.requests.post')
    def test_dropped_connection_is_retried(self, post, _print, sleep):
        post.side_effect = [requests.exceptions.ChunkedEncodingError("Connection broken"),
                            http_response(200, html_page("https://pizza.example"))]
        self.assertIn("https://pizza.example", self.tool.execute(["best antibes pizza"]))
        sleep.assert_called_once_with(2.0)

    @patch('sources.tools.searxSearch.requests.post')
    def test_http_429_is_retried_honouring_retry_after(self, post, _print, sleep):
        post.side_effect = [http_response(429, headers={"Retry-After": "7"}),
                            http_response(200, html_page("https://pizza.example"))]
        result = self.tool.execute(["best antibes pizza"])
        self.assertIn("https://pizza.example", result)
        sleep.assert_called_once_with(7.0)

    @patch('sources.tools.searxSearch.requests.get')
    @patch('sources.tools.searxSearch.requests.post')
    def test_blocked_engines_retry_then_raise(self, post, get, _print, sleep):
        post.return_value = http_response(200, html_page())
        get.return_value = http_response(200, json_body={
            "results": [], "unresponsive_engines": [["google", "Suspended: too many requests"],
                                                    ["duckduckgo", "CAPTCHA"]]})
        with self.assertRaises(AgenticSeekError) as ctx:
            self.tool.execute(["best antibes pizza"])
        self.assertEqual(ctx.exception.title, "Search engines rate limited")
        self.assertIn("google (Suspended: too many requests)", ctx.exception.message)
        self.assertEqual(post.call_count, self.tool.max_attempts)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2.0, 4.0])

    @patch('sources.tools.searxSearch.requests.get')
    @patch('sources.tools.searxSearch.requests.post')
    def test_no_results_with_healthy_engines_raises_without_retry(self, post, get, _print, sleep):
        post.return_value = http_response(200, html_page())
        get.return_value = http_response(200, json_body={"results": [], "unresponsive_engines": []})
        with self.assertRaises(AgenticSeekError) as ctx:
            self.tool.execute(["zzqx nonsense"])
        self.assertEqual(ctx.exception.title, "No search results")
        sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
