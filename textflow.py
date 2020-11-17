"""Code for optimal paragraph line breaking.

The algorithm is described in line-breaking-text-formatting.md,
"On the Line Breaking Problem in Text Formatting" by James O. Achugbue.

The basic idea is to first use the "greedy" line breaker, then shift
some words to subsequent lines, to do a better job of evening out the
number of extra spaces on lines within the paragraph.

The algorithm's complexity is approximately O(n) on the number of
words in the paragraph, but it is somewhat higher than the "greedy"
line breaker.

The algorithm is designed for fixed-width text, but can be fairly
easily extended to work with proportional fonts and to handle
hyphenation.
"""

from dataclasses import dataclass
import sys
from typing import List, Optional

assert sys.version_info >= (3, 9)


@dataclass(frozen=True)
class Word:
    """A word with its attributes."""

    text: str
    width: int
    __slots__ = ['text', 'width']


def as_line_text_list(lines: List[List[Word]]) -> List[List[str]]:
    return [[w.text for w in line] for line in lines]


def text_to_words(text: str, max_width: Optional[int] = None) -> List[Word]:
    """Split arbitrary text into list of Word."""
    return split_text_to_words(split_text(text), max_width)


def split_text_to_words(words: List[str],
                        max_width: Optional[int] = None) -> List[Word]:
    """Transform split text into list of Word.

    If max_width isn't specified, you need to call adjust_words to
    ensure proper behavior by the various text flow algorithms.
    """
    if max_width:
        assert max_width > 0
        return [Word(word, min(max_width, len(word))) for word in words]
    else:
        return [Word(word, len(word)) for word in words]


def split_text(text: str) -> List[str]:
    """Split arbitrary text into words (str)."""
    return text.split()


def adjust_words(words: List[Word], max_width: int) -> List[Word]:
    """Handle extra-long words in list of words."""
    assert max_width > 0
    return [Word(w.text, min(w.width, max_width)) for w in words]


def line_by_line(words: List[Word], max_width: int) -> List[List[Word]]:
    """Greedy algorithm for flowing text in a paragraph.

    Assumes words has run through adjust_words.
    """

    line: List[Word] = []
    lines: List[List[Word]] = []
    line_width = -1
    for word in words:
        line_width += 1 + word.width
        if line_width > max_width:
            lines.append(line)
            line_width = word.width
            line = [word]
        else:
            line.append(word)
    lines.append(line)
    return lines


def line_by_line_reversed(words: List[Word],
                          max_width: int) -> List[List[Word]]:
    """Greedy algorithm for flowing text in a paragraph,
    with the lines being assigned in reverse order.

    Assumes words has run through adjust_words.
    """

    line: List[Word] = []
    lines: List[List[Word]] = []
    line_width = -1
    for word in reversed(words):
        line_width += 1 + word.width
        if line_width > max_width:
            lines.insert(0, line)
            line_width = word.width
            line = [word]
        else:
            line.insert(0, word)
    lines.insert(0, line)
    return lines
