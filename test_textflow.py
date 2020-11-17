"""Test the various algorithms in textflow."""

from textflow import (Word, as_line_text_list, text_to_words,
                      split_text_to_words, split_text, adjust_words,
                      line_by_line)
import unittest


class TestSplit(unittest.TestCase):
    """Test text_to_words, split_text_to_words, etc."""

    maxDiff = None

    text = '''
        He was defenestrated
        without cause.
        '''

    words = ['He', 'was', 'defenestrated', 'without', 'cause.']

    max_word_width = 10

    words_Words = [
        Word('He', 2),
        Word('was', 3),
        Word('defenestrated', 13),
        Word('without', 7),
        Word('cause.', 6),
    ]

    adjust_words_Words = [
        Word('He', 2),
        Word('was', 3),
        Word('defenestrated', max_word_width),
        Word('without', 7),
        Word('cause.', 6),
    ]

    lines_words = [
        [Word('He', 2), Word('was', 3)],
        [Word('defenestrated', max_word_width)],
        [Word('without', 7)],
        [Word('cause.', 6)],
    ]

    lines_text = [
        ['He', 'was'],
        ['defenestrated'],
        ['without'],
        ['cause.'],
    ]

    def test_as_line_text_list(self):
        self.assertEqual(as_line_text_list(self.lines_words), self.lines_text)

    def test_split_text(self):
        self.assertEqual(split_text(self.text), self.words)

    def test_split_text_to_words(self):
        self.assertEqual(split_text_to_words(self.words), self.words_Words)

    def test_text_to_words(self):
        self.assertEqual(text_to_words(self.text), self.words_Words)
        self.assertEqual(text_to_words(self.text, self.max_word_width),
                         self.adjust_words_Words)
        self.assertEqual(adjust_words(self.words_Words, self.max_word_width),
                         self.adjust_words_Words)
        self.assertEqual(
            adjust_words(self.adjust_words_Words, self.max_word_width),
            self.adjust_words_Words)

    def test_line_by_line(self):
        self.assertEqual(
            as_line_text_list(
                line_by_line(text_to_words(self.text, self.max_word_width),
                             self.max_word_width)),
            [['He', 'was'], ['defenestrated'], ['without'], ['cause.']])


if __name__ == '__main__':
    unittest.main()
