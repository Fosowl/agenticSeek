import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.tools.searxSearch import searxSearch

class TestSearxSearch(unittest.TestCase):

    def setUp(self):
        # Set a dummy base URL for initialization
        self.base_url = "http://mock-searx.com"
        self.search_tool = searxSearch(base_url=self.base_url)
        self.valid_query = "test query"

    @patch('os.getenv')
    def test_initialization_with_env_variable(self, mock_getenv):
        # Mock the environment variable
        mock_getenv.return_value = "http://env-searx.com"
        search_tool = searxSearch()
        self.assertEqual(search_tool.base_url, "http://env-searx.com")

    @patch('os.getenv')
    def test_initialization_no_base_url(self, mock_getenv):
        # Mock the environment variable to return None
        mock_getenv.return_value = None
        with self.assertRaises(ValueError):
            searxSearch(base_url=None)

    @patch('requests.post')
    def test_execute_valid_query(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <article class='result'>
            <a class='url_header' href='http://example.com/result1'></a>
            <h3>Title 1</h3>
            <p class='content'>Description 1</p>
        </article>
        """
        mock_post.return_value = mock_response

        result = self.search_tool.execute([self.valid_query])
        self.assertIn("Title:Title 1", result)
        self.assertIn("Snippet:Description 1", result)
        self.assertIn("Link:http://example.com/result1", result)

    def test_execute_empty_query(self):
        result = self.search_tool.execute([""])
        self.assertEqual(result, "Error: Empty search query provided.")

    def test_execute_no_query(self):
        result = self.search_tool.execute([])
        self.assertEqual(result, "Error: No search query provided.")

    @patch('requests.post')
    def test_execute_request_exception(self, mock_post):
        # Configure the mock to raise a RequestException
        mock_post.side_effect = requests.exceptions.RequestException("Test error")

        with self.assertRaises(Exception) as context:
            self.search_tool.execute([self.valid_query])
        self.assertIn("Searxng search failed", str(context.exception))

    @patch('requests.post')
    def test_execute_no_results(self, mock_post):
        # Mock a response with no results
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_post.return_value = mock_response

        result = self.search_tool.execute(["query with no results"])
        self.assertEqual(result, "No search results, web search failed.")

    def test_execution_failure_check_error(self):
        output = "Error: Something went wrong"
        self.assertTrue(self.search_tool.execution_failure_check(output))

    def test_execution_failure_check_no_error(self):
        output = "Search completed successfully"
        self.assertFalse(self.search_tool.execution_failure_check(output))

if __name__ == '__main__':
    unittest.main()
