"""Code for optimal paragraph line breaking.

The algorithm is described in line-breaking-text-formatting.md,
"On the Line Breaking Problem in Text Formatting" by James O. Achugbue.

The basic idea is to first use the "greedy" line breaker, then shift
some words to subsequent lines, to do a better job of evening out the
number of extra spaces on lines within the paragraph.

The algorithm's time complexity is slightly worse than O(N) on the
number of words in the paragraph, but it is higher than the "greedy"
line breaker (two "greedy" passes and iteration over the line
end "slacks"). It is also O(N) in space.

The algorithm is designed for fixed-width text, but can be fairly
easily extended to work with proportional fonts and to handle
hyphenation. To allow this, the API allows specifying a list of words
with custom-computed widths.
"""

# TODO: pytype -V 3.8 --protocols --precise-return --check-attribute-types --check-container-types --check-parameter-types --check-variable-types textflow.py

import functools
import sys
from typing import Any, Callable, Iterable, List, Optional, Type, TypeVar

assert sys.version_info >= (3, 8)  # TODO: 3.9 (pytype doesn't support 3.9)

# INFINITE is any number larger than maximum
INFINITE = sys.float_info.max


class Word(tuple):
    """A word with its attributes (width).

    text: str
    width: int
    """

    def __new__(cls: Type['Word'], text: str, width: int) -> 'Word':
        """Create a Word object (immutable)."""
        return tuple.__new__(cls, (text, width))

    def __init__(self, text: str, width: int) -> None:
        """A do-nothing __init__ to make pytype happy."""
        pass

    @property
    def text(self) -> str:
        """Alias Word.text."""
        return self[0]

    def width_min(self, max_width: int) -> int:
        """Get Word.width, but no larger than max_width."""
        return min(self[1], max_width)

    def __eq__(self, other: Any) -> bool:
        """Equality test - only used in unit tests."""
        return isinstance(other, Word) and tuple.__eq__(self, other)

    def __repr__(self) -> str:
        """String representation of a Word(text, width)."""
        return f'Word({self.text!r}, {self.width!r})'


T1 = TypeVar('T1')
T2 = TypeVar('T2')


def map_line_words(
    fn: Callable[[T1], T2], list_of_lines: Iterable[Iterable[T1]]
) -> List[List[T2]]:
    """Apply fn to each word in list_of_lines."""
    return [[fn(word) for word in line] for line in list_of_lines]


def indexes_to_words(
    line_indexes: Callable[[List[Word], int, int], List[List[int]]],
    words: List[Word],
    max_width: int,
    space_width=1,
) -> List[List[Word]]:
    """Apply line_indexes algorithm (with max_width lines) to words, outputting lines of Word's."""
    return map_line_words(lambda i: words[i], line_indexes(words, max_width, space_width))


def indexes_to_texts(
    line_indexes: Callable[[List[Word], int, int], List[List[int]]],
    words: List[Word],
    max_width: int,
    space_width=1,
) -> List[List[str]]:
    """Apply line_indexes algorithm (with max_width lines) to words, outputting lines of str's."""
    return map_line_words(lambda i: words[i].text, line_indexes(words, max_width, space_width))


def text_to_text_lines(
    line_indexes: Callable[[List[Word], int, int], List[List[int]]],
    text: str,
    max_width: int,
    space_width=1,
) -> List[List[str]]:
    """Apply line_indexes algorithm (with max_width lines) to text, outputting lines of str's."""
    return indexes_to_texts(line_indexes, text_to_words(text), max_width, space_width)


def optimal_line_indexes(words: List[Word], max_width: int, space_width=1) -> List[List[int]]:
    """Optimal algorithm for flowing text in a paragraph."""

    lines_fwd = line_by_line_indexes(words, max_width)
    lines_bck = line_by_line_reversed_indexes(words, max_width)
    assert len(lines_fwd) == len(lines_bck)
    assert all(fwd >= bck for fwd, bck in zip(lines_fwd, lines_bck))

    # optimal_break[I]: is optimal line start for line I (0-origin into words)
    optimal_break = len(lines_fwd) * [-1]  # An invalid index
    optimal_break[0] = 0
    if len(lines_fwd) > 1:
        optimal_break[-1] = lines_fwd[-1][0]
    else:
        assert lines_fwd == lines_bck
        return lines_fwd

    # cost[i] is cost function = C[(i,len(words)], i ranging over indexes of words
    #     where C is the cost function from the "DYNAMIC" algorithm.
    cost = len(words) * [INFINITE]
    cost[lines_fwd[-1][0]] = 2.0

    # loop on lines backwards
    for lineno in reversed(range(0, len(lines_fwd) - 1)):
        line_len = (
            functools.reduce(
                lambda total, width: total + space_width + width,
                (words[i].width_min(max_width) for i in lines_fwd[lineno]),
            )
            - words[lines_fwd[lineno][0]].width_min(max_width)
        )

        # loop over lineno-th slack
        for slack in reversed(range(lines_bck[lineno][0], lines_fwd[lineno][0] + 1)):
            line_len = line_len + space_width + words[slack].width_min(max_width)
            line_and_slack_len = (
                line_len + space_width + words[lines_fwd[lineno + 1][0]].width_min(max_width)
            )
            # cost[slack] has been already initialized to INFINITE

            # loop over (lineno+1)-th slack
            for slack_n1 in reversed(
                range(lines_bck[lineno + 1][0], lines_fwd[lineno + 1][0] + 1)
            ):
                line_and_slack_len = (
                    line_and_slack_len - space_width - words[slack_n1].width_min(max_width)
                )
                if line_and_slack_len <= max_width:
                    # update cost[slack]  # TODO: see Notes.md#Cost_function
                    new_cost = (1.0 + 1.0 / line_and_slack_len) * cost[slack_n1]
                    if new_cost < cost[slack]:
                        cost[slack] = new_cost
                        optimal_break[lineno + 1] = slack_n1
            # print('***', dict(lineno=lineno, slack=slack, slack_n1=slack_n1, optimal={lineno+1:optimal_break[lineno+1]}, cost={i:c for i,c in enumerate(cost) if c != INFINITE}))  # DO NOT SUBMIT

    return [list(range(i, j)) for i, j in zip(optimal_break, optimal_break[1:])] + [
        list(range(lines_fwd[-1][0], len(words)))
    ]


def text_to_words(text: str) -> List[Word]:
    """Split arbitrary text into list of Word."""
    return split_text_to_words(split_text(text))


def split_text_to_words(words: Iterable[str]) -> List[Word]:
    """Transform split text into list of Word."""
    return [Word(word, len(word)) for word in words]


def split_text(text: str) -> List[str]:
    """Split arbitrary text into words (str)."""
    return text.split()


def line_by_line_indexes(words: Iterable[Word], max_width: int, space_width=1) -> List[List[int]]:
    """Greedy algorithm for flowing text in a paragraph - returns indexes into words.

    Assumes words has been run through adjust_words or produced by
    split_text_to_words with max_width specified.
    """
    curr_line: List[int] = []
    lines: List[List[int]] = []
    line_width = -space_width
    for i, word in enumerate(words):
        line_width += space_width + word.width_min(max_width)
        if line_width > max_width:
            lines.append(curr_line)
            line_width = word.width_min(max_width)
            curr_line = [i]
        else:
            curr_line.append(i)
    lines.append(curr_line)
    return lines


def line_by_line_reversed_indexes(
    words: List[Word], max_width: int, space_width=1
) -> List[List[int]]:
    """Greedy algorithm for flowing text in a paragraph, with the lines
    being assigned in reverse order - returns indexes into words.

    Assumes words has been run through adjust_words or produced by
    split_text_to_words with max_width specified.
    """
    curr_line: List[int] = []
    lines: List[List[int]] = []
    line_width = -space_width
    for i, word in reversed(list(enumerate(words))):
        line_width += space_width + word.width_min(max_width)
        if line_width > max_width:
            lines.insert(0, curr_line)
            line_width = word.width_min(max_width)
            curr_line = [i]
        else:
            curr_line.insert(0, i)
    lines.insert(0, curr_line)
    return lines
