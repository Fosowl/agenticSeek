import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.utility import get_color_map


class TestUtility(unittest.TestCase):
    """Test suite for utility module functions."""

    def test_get_color_map_returns_dict(self):
        """Test that get_color_map returns a dictionary."""
        color_map = get_color_map()
        self.assertIsInstance(color_map, dict)

    def test_get_color_map_has_required_keys(self):
        """Test that color map contains all required color keys."""
        color_map = get_color_map()
        required_keys = ["success", "failure", "status", "code", "warning", "output", "info"]
        for key in required_keys:
            self.assertIn(key, color_map, f"Missing key: {key}")

    def test_get_color_map_values_are_strings(self):
        """Test that all color values are strings."""
        color_map = get_color_map()
        for key, value in color_map.items():
            self.assertIsInstance(value, str, f"Value for '{key}' should be a string")

    def test_success_is_green(self):
        """Test that success maps to green."""
        color_map = get_color_map()
        self.assertEqual(color_map["success"], "green")

    def test_failure_is_red(self):
        """Test that failure maps to red."""
        color_map = get_color_map()
        self.assertEqual(color_map["failure"], "red")


if __name__ == '__main__':
    unittest.main()
