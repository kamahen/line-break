"""Break/join/adjust lines based on spacing."""


import textwrap


def lines_of_words(S, W, text_words):
    """Convert index of first words to list of lines

    Take the "S" that's computed by a line breaking algorithm and
    converts it to a list of lines, where each line is a list of
    words.
    """

    assert sorted(S.keys()) == list(range(1, 1+max(S.keys()))), [
        sorted(S.keys()), list(range(1, 1+max(S.keys())))]
    return [line_words(S, W, text_words, i) for i in sorted(S.keys())]


def line_words(S, W, text_words, i):
    """Return list of words line (S[I]: index of first word in i-th line)."""

    j = i + 1
    w_i = (range(S[i], S[j]) if j in S else
           range(S[i], max(W.keys()) + 1))
    return [text_words[k-1] for k in w_i]


def distribute_spaces(words, D, left_to_right):
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


def split_paragraphs(text):
    """Split text into a list of paragraphs. Assumes Unix-style lines."""

    para = []
    for line in text.split('\n'):
        if line == '':
            if para:
                yield '\n'.join(para)
            para = []
        else:
            para.append(line)
    if para:
        yield '\n'.join(para)



def text_to_list_of_lines(text):
    """Convert text into a list of lines, each being a list of words."""
    return [line.split() for line in textwrap.dedent(text.strip()).split('\n')]
