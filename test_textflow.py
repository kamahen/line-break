"""Test the various algorithms in textflow."""

from textflow import (Word, as_line_text_list, text_to_words,
                      split_text_to_words, split_text, adjust_words,
                      line_by_line, line_by_line_reversed)
import unittest


class TestSplit(unittest.TestCase):
    """Test text_to_words, split_text_to_words, etc."""

    maxDiff = None

    text = '''
        He was defenestrated
        without cause.
        '''

    words = ['He', 'was', 'defenestrated', 'without', 'cause.']

    max_line_width = 10

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
        Word('defenestrated', max_line_width),
        Word('without', 7),
        Word('cause.', 6),
    ]

    lines_words = [
        [Word('He', 2), Word('was', 3)],
        [Word('defenestrated', max_line_width)],
        [Word('without', 7)],
        [Word('cause.', 6)],
    ]

    lines_text = [
        ['He', 'was'],
        ['defenestrated'],
        ['without'],
        ['cause.'],
    ]

    # The sample text from the paper (greedy breaks):

    PAPER_TEXT = """
      We  live in a print-oriented society. Every day
      we produce a huge volume of  printed  material,
      ranging   from  handbills  to  heavy  reference
      books.   Despite   the   mushroom   growth   of
      electronic   media,   print  remains  the  most
      versatile and most widely used medium for  mass
      communication.
    """

    PAPER_EXPECTED_TEXT = """
      We  live  in  a  print-oriented  society. Every
      day  we  produce  a  huge  volume  of   printed
      material,   ranging  from  handbills to   heavy
      reference books. Despite  the  mushroom  growth
      of  electronic  media,  print  remains the most
      versatile and most widely used medium for  mass
      communication.
    """

    # maximum number of characters per line in the paper
    PAPER_MAX_LINE_WIDTH = 47

    def test_as_line_text_list(self):
        self.assertEqual(as_line_text_list(self.lines_words), self.lines_text)

    def test_split_text(self):
        self.assertEqual(split_text(self.text), self.words)

    def test_split_text_to_words(self):
        self.assertEqual(split_text_to_words(self.words), self.words_Words)

    def test_text_to_words(self):
        self.assertEqual(text_to_words(self.text), self.words_Words)
        self.assertEqual(text_to_words(self.text, self.max_line_width),
                         self.adjust_words_Words)
        self.assertEqual(adjust_words(self.words_Words, self.max_line_width),
                         self.adjust_words_Words)
        self.assertEqual(
            adjust_words(self.adjust_words_Words, self.max_line_width),
            self.adjust_words_Words)

    def test_line_by_line(self):
        self.assertEqual(
            as_line_text_list(
                line_by_line(text_to_words(self.text, self.max_line_width),
                             self.max_line_width)),
            [['He', 'was'], ['defenestrated'], ['without'], ['cause.']])
        self.assertEqual(
            as_line_text_list(
                line_by_line_reversed(
                    text_to_words(self.text, self.max_line_width),
                    self.max_line_width)),
            [['He', 'was'], ['defenestrated'], ['without'], ['cause.']])

        paper_greedy_lines = as_line_text_list(
            line_by_line(
                text_to_words(self.PAPER_TEXT, self.PAPER_MAX_LINE_WIDTH),
                self.PAPER_MAX_LINE_WIDTH))
        paper_expected_greedy_lines = [
            line.split() for line in self.PAPER_TEXT.strip().split('\n')
        ]
        self.assertTrue(
            all(
                len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH
                for line in paper_expected_greedy_lines))
        self.assertTrue(
            all(
                len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH
                for line in paper_greedy_lines))
        self.assertEqual(paper_greedy_lines, paper_expected_greedy_lines)
        self.assertTrue(
            all(
                len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH
                for line in as_line_text_list(
                    line_by_line_reversed(
                        text_to_words(self.PAPER_TEXT,
                                      self.PAPER_MAX_LINE_WIDTH),
                        self.PAPER_MAX_LINE_WIDTH))))


if __name__ == '__main__':
    unittest.main()
