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

# TODO: restore the type annotations (removed for testing pytype)

import functools
import sys
from typing import List, Optional

assert sys.version_info >= (3, 7)

# INFINITE is any number larger than maximum
INFINITE = sys.float_info.max


# @dataclass(frozen=True)  # TODO: restore this
# class Word:
#     """A word with its attributes."""

#     text: str
#     width: int
#     __slots__ = ['text', 'width']

class Word:  # TODO: use @dataclass(frozen=True)
    """A word with its attributes."""

    __slots__ = ['text', 'width']

    # def __init__(self, text: str, width: int) -> None:  # TODO: restore
    def __init__(self, text, width):
        self.text = text
        self.width = width

    # def __eq__(self, other: Any) -> bool:  # TODO: restore
    def __eq__(self, other):
        return isinstance(other, Word) and self.text == other.text and self.width == other.width

    def __repr__(self):
        return f'Word({self.text!r}, width={self.width!r})'


def map_line_words(fn, list_of_lines):
    """Apply fn to each word in list_of_lines."""

    return [[fn(word) for word in line] for line in list_of_lines]


# def indexes_to_words(fn, words: List[Word], max_width: int, space_width=1) -> List[List[Word]]:  # TODO: restore
def indexes_to_words(fn, words, max_width, space_width=1):
    return map_line_words(lambda i: words[i], fn(words, max_width, space_width))


# def indexes_to_texts(fn, words: List[Word], max_width: int, space_width=1) -> List[List[str]]:  # TODO: restore
def indexes_to_texts(fn, words, max_width, space_width=1):
    return map_line_words(lambda i: words[i].text, fn(words, max_width, space_width))


# def optimal_line_indexes(words: List[Word], max_width: int, space_width=1) -> List[List[int]]:  # TODO: restore
def optimal_line_indexes(words, max_width, space_width=1):
    """Optimal algorithm for flowing text in a paragraph.

    Assumes words has run through adjust_words.
    """

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
                (words[i].width for i in lines_fwd[lineno]),
            )
            - words[lines_fwd[lineno][0]].width
        )

        # loop over lineno-th slack
        for slack in reversed(range(lines_bck[lineno][0], lines_fwd[lineno][0] + 1)):
            line_len = line_len + space_width + words[slack].width
            line_and_slack_len = line_len + space_width + words[lines_fwd[lineno + 1][0]].width
            # cost[slack] has been already initialized to INFINITE

            # loop over (lineno+1)-th slack
            for slack_n1 in reversed(range(lines_bck[lineno + 1][0], lines_fwd[lineno + 1][0] + 1)):
                line_and_slack_len = line_and_slack_len - space_width - words[slack_n1].width
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


# def text_to_words(text: str, max_width: Optional[int] = None) -> List[Word]:  # TODO: restore
def text_to_words(text, max_width=None):
    """Split arbitrary text into list of Word."""
    return split_text_to_words(split_text(text), max_width)


# def split_text_to_words(words: List[str], max_width: Optional[int] = None) -> List[Word]:  # TODO: restore
def split_text_to_words(words, max_width=None):
    """Transform split text into list of Word.

    If max_width isn't specified, you need to call adjust_words to
    ensure proper behavior by the various text flow algorithms.
    """
    if max_width:
        assert max_width > 0
        return [Word(word, min(max_width, len(word))) for word in words]
    else:
        return [Word(word, len(word)) for word in words]


# def split_text(text: str) -> List[str]:  # TODO: restore
def split_text(text):
    """Split arbitrary text into words (str)."""
    return text.split()


# def adjust_words(words: List[Word], max_width: int) -> List[Word]:  # TODO: restore
def adjust_words(words, max_width):
    """Handle extra-long words in list of words."""
    assert max_width > 0
    return [Word(w.text, min(w.width, max_width)) for w in words]


# def line_by_line_indexes(words: List[Word], max_width: int, space_width=1) -> List[List[int]]:  # TODO: restore
def line_by_line_indexes(words, max_width, space_width=1):
    """Greedy algorithm for flowing text in a paragraph - returns indexes into words.

    Assumes words has run through adjust_words.
    """
    # curr_line: List[int] = []  # TODO: restore
    # lines: List[List[int]] = []  # TODO: restore
    curr_line = []
    lines = []
    line_width = -space_width
    for i, word in enumerate(words):
        line_width += space_width + word.width
        if line_width > max_width:
            lines.append(curr_line)
            line_width = word.width
            curr_line = [i]
        else:
            curr_line.append(i)
    lines.append(curr_line)
    return lines


def line_by_line_reversed_indexes(words: List[Word], max_width: int, space_width=1) -> List[List[int]]:
    """Greedy algorithm for flowing text in a paragraph, with the lines
    being assigned in reverse order - returns indexes into words.

    Assumes words has run through adjust_words.
    """
    # curr_line: List[int] = []  # TODO: restore
    # lines: List[List[int]] = []  # TODO: restore
    curr_line = []
    lines = []
    line_width = -space_width
    for i, word in reversed(list(enumerate(words))):
        line_width += space_width + word.width
        if line_width > max_width:
            lines.insert(0, curr_line)
            line_width = word.width
            curr_line = [i]
        else:
            curr_line.insert(0, i)
    lines.insert(0, curr_line)
    return lines


if __name__ == '__main__':
    # For pytype, except it doesn't seem to trigger anything
    assert indexes_to_texts(optimal_line_indexes, text_to_words('', 10), 10) == [[]]
