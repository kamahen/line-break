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

from dataclasses import dataclass
import functools
import sys
from typing import List, Optional

assert sys.version_info >= (3, 9)

# INFINITE is any number larger than maximum
INFINITE = sys.float_info.max


@dataclass(frozen=True)
class Word:
    """A word with its attributes."""

    text: str
    width: int
    __slots__ = ['text', 'width']


def map_line_words(fn, list_of_lines):
    """Apply fn to each word in list_of_lines."""

    return [[fn(word) for word in line] for line in list_of_lines]


def indexes_to_words(
    fn, words: List[Word], max_width: int, space_width=1
) -> List[List[Word]]:
    return map_line_words(lambda i: words[i], fn(words, max_width, space_width))


def indexes_to_texts(
    fn, words: List[Word], max_width: int, space_width=1
) -> List[List[Word]]:
    return map_line_words(lambda i: words[i].text, fn(words, max_width, space_width))


def optimal_line_indexes(
    words: List[Word], max_width: int, space_width=1
) -> List[List[int]]:
    """Optimal algorithm for flowing text in a paragraph.

    Assumes words has run through adjust_words.
    """

    lines_fwd = line_by_line_indexes(words, max_width)
    lines_bck = line_by_line_reversed_indexes(words, max_width)
    assert len(lines_fwd) == len(lines_bck)
    assert all(fwd >= bck for fwd, bck in zip(lines_fwd, lines_bck))

    # cost[i] is cost function = C[(i,len(words)], i ranging over indexes of words
    cost = {lines_fwd[-1][0]: 2.0}

    # c = {J: 2.0 for J in from_to(1, self.N)}  # <==== TODO: is this correct, to avoid 'K in c' test below?
    # optimal_break[I]: is optimal line start for line I (0-origin into words)
    optimal_break = {0: 0, len(lines_fwd) - 1: lines_fwd[-1][0]}

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
        for lineno_slack in reversed(
            range(lines_bck[lineno][0], lines_fwd[lineno][0] + 1)
        ):
            line_len = line_len + space_width + words[lineno_slack].width
            line_and_slack_len = (
                line_len + space_width + words[lines_fwd[lineno + 1][0]].width
            )
            cost[lineno_slack] = INFINITE

            # loop over (lineno+1)-th slack
            assert lines_fwd[lineno + 1] >= lines_bck[lineno + 1]
            for lineno_next_slack in reversed(
                range(lines_bck[lineno + 1][0], lines_fwd[lineno + 1][0] + 1)
            ):
                line_and_slack_len = (
                    line_and_slack_len - space_width - words[lineno_next_slack].width
                )
                # TODO: added 'if lineno_next_slack in c'
                if line_and_slack_len <= max_width and lineno_next_slack in cost:
                    # update cost[lineno_slack]  # TODO: see Notes.md#Cost_function
                    new_cost = (1.0 + 1.0 / line_and_slack_len) * cost[
                        lineno_next_slack
                    ]
                    if new_cost < cost[lineno_slack]:
                        cost[lineno_slack] = new_cost
                        optimal_break[lineno + 1] = lineno_next_slack

    return [
        list(
            range(
                optimal_break[i],
                optimal_break[i + 1] if i + 1 in optimal_break else len(words),
            )
        )
        for i in sorted(optimal_break)
    ]


def text_to_words(text: str, max_width: Optional[int] = None) -> List[Word]:
    """Split arbitrary text into list of Word."""
    return split_text_to_words(split_text(text), max_width)


def split_text_to_words(
    words: List[str], max_width: Optional[int] = None
) -> List[Word]:
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


def line_by_line_indexes(
    words: List[Word], max_width: int, space_width=1
) -> List[List[int]]:
    """Greedy algorithm for flowing text in a paragraph - returns indexes into words.

    Assumes words has run through adjust_words.
    """
    line: List[int] = []
    lines: List[List[int]] = []
    line_width = -space_width
    for i, word in enumerate(words):
        line_width += space_width + word.width
        if line_width > max_width:
            lines.append(line)
            line_width = word.width
            line = [i]
        else:
            line.append(i)
    lines.append(line)
    return lines


def line_by_line_reversed_indexes(
    words: List[Word], max_width: int, space_width=1
) -> List[List[int]]:
    """Greedy algorithm for flowing text in a paragraph, with the lines
    being assigned in reverse order - returns indexes into words.

    Assumes words has run through adjust_words.
    """
    line: List[int] = []
    lines: List[List[int]] = []
    line_width = -space_width
    for i, word in reversed(list(enumerate(words))):
        line_width += space_width + word.width
        if line_width > max_width:
            lines.insert(0, line)
            line_width = word.width
            line = [i]
        else:
            line.insert(0, i)
    lines.insert(0, line)
    return lines
