import unittest

from sources.echo_filter import filter_echo, is_echo


class TestEchoFilter(unittest.TestCase):
    def test_partial_words_do_not_discard_user_speech(self):
        for text, spoken in [
            ("he likes art", "she likes artists"),
            ("she likes artists", "he likes art"),
            ("go now please", "algo now pleased"),
        ]:
            with self.subTest(text=text, spoken=spoken):
                self.assertFalse(is_echo(text, spoken))
                self.assertEqual(filter_echo(text, spoken), text)

    def test_consecutive_words_still_detect_echo(self):
        for text, spoken in [
            ("the result is ready", "the result is ready"),
            ("  THE result is ready  ", "the result is ready"),
            ("please the result is ready now", "the result is ready"),
            ("the result is ready", "please the result is ready now"),
            ("yes that works", "yes that works."),
            ("yes that works.", "yes that works"),
        ]:
            with self.subTest(text=text, spoken=spoken):
                self.assertTrue(is_echo(text, spoken))
                self.assertEqual(filter_echo(text, spoken), "")

    def test_short_or_unrelated_text_is_kept(self):
        for text, spoken in [
            ("", "the result is ready"),
            ("the result is ready", ""),
            ("the result", "the result is ready"),
            ("please try again", "the result is ready"),
        ]:
            with self.subTest(text=text, spoken=spoken):
                self.assertFalse(is_echo(text, spoken))
                self.assertEqual(filter_echo(text, spoken), text)


if __name__ == "__main__":
    unittest.main()
