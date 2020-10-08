"""Code in line-breaking-text-formatting.md, transcribed to Python

The original variable names have been retained, but we use dicts
rather than arrays, to handle the 1-origin indexing of the algorithms.

The code requires Python 3.7 or later, to take advantage of the
ordering of a dict iterator being the same as collections.OrderedDict.
"""


# The sample text:

SAMPLE_TEXT = """
  We  live in a print-oriented society. Every day
  we produce a huge volume of  printed  material,
  ranging   from  handbills  to  heavy  reference
  books.   Despite   the   mushroom   growth   of
  electronic   media,   print  remains  the  most
  versatile and most widely used medium for  mass
  communication.
"""

# The sample text words, with a dummy item at the beginning
SAMPLE_TEXT_WORDS = SAMPLE_TEXT.split()

# N: number of words in paragraph
N = len(SAMPLE_TEXT_WORDS)

# D: maximum number of characters per line
D = 47

# W: number of characters in the I-th word (0-origin)
W = {i+1:len(word) for i, word in enumerate(SAMPLE_TEXT_WORDS)}


def line_by_line():
    """compute S: index of first word in I-the line"""
    # initialize
    M = 1
    S = {1:1}
    L = {M:W[1]}

    for I in range(2, N+1):
        # add next word to current line
        L[M] = L[M] + 1 + W[I]

        if L[M] > D:
            L[M] = L[M] - 1 - W[I]

            # start new line
            M = M + 1
            S[M] = I
            L[M] = W[I]

    return S


def lines_of_words(S):
    """Convert index of first words to list of lines

    This function is not in the original paper; it has been added here
    to handle the output nicely. It takes the "S" that's computed by a
    line breaking algorithm and converts it to a list of lines, where
    each line is a list of words.
    """

    assert sorted(S.keys()) == list(range(1, 1+max(S.keys())))
    return [_line_words(S, i) for i in sorted(S.keys())]


def _line_words(S, i):
    """Return list of words line (S[I]: index of first word in i-th line)."""

    j = i + 1
    w_i = range(S[i], S[j]) if j in S else range(S[i], max(W.keys()) + 1)
    return [SAMPLE_TEXT_WORDS[k-1] for k in w_i]


def distribute_spaces(words, left_to_right):
    """words: list of words in line
    left_to_right: which direction to add blanks
    Returns: list of lines with blanks inserted
    """

    if len(words) <= 1:
        return ' '.join(words)

    # TODO: make this more functional
    to_distribute = D - len(' '.join(words))

    if left_to_right:
        i_range = lambda: range(0, len(words) - 1)
        pad_word = lambda w: w + ' '
    else:
        i_range = lambda: range(len(words) - 1, 0, -1)
        pad_word = lambda w: ' ' + w

    padded_words = words
    while to_distribute > 0:
        for i in i_range():
            padded_words[i] = pad_word(padded_words[i])
            to_distribute -= 1
            if to_distribute <= 0:
                break
    return ' '.join(padded_words)

S = line_by_line()
S_words = lines_of_words(S)
print('\n'.join(distribute_spaces(line, i % 2 == 0)
                for i, line in enumerate(S_words)))
