"""Test the various algorithms in textflow."""

import functools
from typing import List
import unittest
from textflow import (
    Word,
    adjust_words,
    indexes_to_texts,
    line_by_line_indexes,
    line_by_line_reversed_indexes,
    optimal_line_indexes,
    split_text,
    split_text_to_words,
    text_to_text_lines,
    text_to_words,
)


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

    PAPER_TEXT = '''
      We  live in a print-oriented society. Every day
      we produce a huge volume of  printed  material,
      ranging   from  handbills  to  heavy  reference
      books.   Despite   the   mushroom   growth   of
      electronic   media,   print  remains  the  most
      versatile and most widely used medium for  mass
      communication.
    '''

    PAPER_EXPECTED_TEXT = '''
      We  live  in  a  print-oriented  society. Every
      day  we  produce  a  huge  volume  of   printed
      material,   ranging  from  handbills to   heavy
      reference books. Despite  the  mushroom  growth
      of  electronic  media,  print  remains the most
      versatile and most widely used medium for  mass
      communication.
    '''

    # maximum number of characters per line in the paper
    PAPER_MAX_LINE_WIDTH = 47

    def test_split_text(self):
        self.assertEqual(split_text(''), [])
        self.assertEqual(split_text(self.text), self.words)

    def test_split_text_to_words(self):
        self.assertEqual(split_text_to_words([]), [])
        self.assertEqual(split_text_to_words(self.words), self.words_Words)

    def test_text_to_words(self):
        self.assertEqual(text_to_words(''), [])
        self.assertEqual(text_to_words('', self.max_line_width), [])
        self.assertEqual(text_to_words(self.text), self.words_Words)
        self.assertEqual(
            text_to_words(self.text, self.max_line_width),
            self.adjust_words_Words,
        )
        self.assertEqual(
            adjust_words(self.words_Words, self.max_line_width),
            self.adjust_words_Words,
        )
        self.assertEqual(adjust_words([], self.max_line_width), [])
        self.assertEqual(
            adjust_words(self.adjust_words_Words, self.max_line_width),
            self.adjust_words_Words,
        )

    def test_line_by_line(self):
        self.assertEqual(
            line_by_line_indexes(text_to_words('', self.max_line_width), self.max_line_width),
            [[]],
        )
        self.assertEqual(
            indexes_to_texts(
                line_by_line_indexes,
                text_to_words('', self.max_line_width),
                self.max_line_width,
            ),
            [[]],
        )
        self.assertEqual(
            line_by_line_reversed_indexes(
                text_to_words('', self.max_line_width), self.max_line_width
            ),
            [[]],
        )
        self.assertEqual(
            indexes_to_texts(
                line_by_line_reversed_indexes,
                text_to_words('', self.max_line_width),
                self.max_line_width,
            ),
            [[]],
        )

        self.assertEqual(
            line_by_line_indexes(
                text_to_words(self.text, self.max_line_width), self.max_line_width
            ),
            [[0, 1], [2], [3], [4]],
        )
        self.assertEqual(
            indexes_to_texts(
                line_by_line_indexes,
                text_to_words(self.text, self.max_line_width),
                self.max_line_width,
            ),
            [['He', 'was'], ['defenestrated'], ['without'], ['cause.']],
        )
        self.assertEqual(
            line_by_line_reversed_indexes(
                text_to_words(self.text, self.max_line_width), self.max_line_width
            ),
            [[0, 1], [2], [3], [4]],
        )
        self.assertEqual(
            indexes_to_texts(
                line_by_line_reversed_indexes,
                text_to_words(self.text, self.max_line_width),
                self.max_line_width,
            ),
            [['He', 'was'], ['defenestrated'], ['without'], ['cause.']],
        )

        paper_text_words = text_to_words(self.PAPER_TEXT, self.PAPER_MAX_LINE_WIDTH)
        paper_greedy_lines_index = line_by_line_indexes(
            paper_text_words, self.PAPER_MAX_LINE_WIDTH
        )
        self.assertEqual(
            functools.reduce(lambda total, x: total + x, paper_greedy_lines_index),
            list(range(0, len(paper_text_words))),
        )

        paper_greedy_lines = indexes_to_texts(
            line_by_line_indexes, paper_text_words, self.PAPER_MAX_LINE_WIDTH
        )
        paper_expected_greedy_lines = text_to_list_of_lines(self.PAPER_TEXT)
        self.assertTrue(
            all(
                len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH
                for line in paper_expected_greedy_lines
            )
        )
        self.assertTrue(
            all(len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH for line in paper_greedy_lines)
        )
        self.assertEqual(paper_greedy_lines, paper_expected_greedy_lines)
        self.assertTrue(
            all(
                len(' '.join(line)) <= self.PAPER_MAX_LINE_WIDTH
                for line in indexes_to_texts(
                    line_by_line_reversed_indexes,
                    text_to_words(self.PAPER_TEXT, self.PAPER_MAX_LINE_WIDTH),
                    self.PAPER_MAX_LINE_WIDTH,
                )
            )
        )

    def test_optimal_lines(self):
        self.assertEqual(
            optimal_line_indexes(text_to_words('', self.max_line_width), self.max_line_width),
            [[]],
        )
        self.assertEqual(
            indexes_to_texts(
                optimal_line_indexes,
                text_to_words('', self.max_line_width),
                self.max_line_width,
            ),
            [[]],
        )
        self.assertEqual(
            optimal_line_indexes(text_to_words('12345', 5), 5),
            [[0]],
        )
        self.assertEqual(
            indexes_to_texts(
                optimal_line_indexes,
                text_to_words('123456', 5),
                5,
            ),
            [['123456']],
        )
        self.assertEqual(
            text_to_text_lines(
                optimal_line_indexes,
                '123456', 5),
            [['123456']])

        paper_text_words = text_to_words(self.PAPER_TEXT, self.PAPER_MAX_LINE_WIDTH)
        paper_optimal_lines = indexes_to_texts(
            optimal_line_indexes, paper_text_words, self.PAPER_MAX_LINE_WIDTH
        )

        paper_expected_optimal_lines = text_to_list_of_lines(self.PAPER_EXPECTED_TEXT)
        self.assertEqual(paper_optimal_lines, paper_expected_optimal_lines)


def text_to_list_of_lines(text: str) -> List[List[str]]:
    """Convert text into a list of (Unix-style) lines, each being a list of words."""
    # TODO: move this to main module
    return [line.split() for line in text.strip().split('\n')]


if __name__ == '__main__':
    unittest.main()
