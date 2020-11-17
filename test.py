"""Test line_break_from_paper."""

# pylint: disable=invalid-name,fixme,line-too-long,bad-whitespace,too-many-instance-attributes,missing-function-docstring

import line_break_from_paper
import line_adjust


# The sample text from the paper:

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

# D: maximum number of characters per line
PAPER_D = 47


PARAS = """
A line
Another line

Start new para

Another para
with a 2nd line
"""

PARAS_SPLIT_EXPECTED = ['A line\nAnother line', 'Start new para', 'Another para\nwith a 2nd line']


def test_sample_text(sample_text, sample_expected_text, sample_d):
    print('test_sample_text', sample_d, '\n-----\n', sample_text, '\n----- (expected)\n', sample_expected_text, '\n-----')
    l_b = line_break_from_paper.LineBreak(sample_text.split(), sample_d)

    l_b.LINE_BY_LINE()
    l_b.LINE_BY_LINE_reversed()
    print('========== line-by-line')
    print(line_adjust.pad_lines(
        lines_of_words(l_b.S, l_b.W, l_b.text_words),
        sample_d))
    # print('W:', l_b.W)
    print('words:', {i: (l_b.W[i], l_b.text_words[i-1]) for i in sorted(l_b.W.keys())})
    print('S:', dd(l_b.S))
    print('E:', dd(l_b.E))
    print('========== S')
    print(lines_of_words(l_b.S, l_b.W, l_b.text_words))
    print('========== E')
    print(lines_of_words(l_b.E, l_b.W, l_b.text_words))
    print('==========')

    l_b.DYNAMIC()
    print('DYNAMIC:', len(l_b.S_dyn), dd(l_b.S_dyn))
    # print('C[(*,N]:', {i:(l_b.text_word(i), l_b.C[(i,l_b.N]) for i in from_to(1, l_b.N)})
    print('========== DYNAMIC')
    l_b_DYNAMIC_words = lines_of_words(l_b.S_dyn, l_b.W, l_b.text_words)
    print(l_b_DYNAMIC_words)
    print('==========')
    print(line_adjust.pad_lines(l_b_DYNAMIC_words, sample_d))
    print('==========')

    l_b.LINE_BREAKER()
    print('LINE_BREAKER:', len(l_b.P), dd(l_b.P))
    print('==========')
    l_b_LINE_BREAKER_words = lines_of_words(l_b.P, l_b.W, l_b.text_words)
    print(line_adjust.pad_lines(l_b_LINE_BREAKER_words, sample_d))
    print('==========')
    if l_b.P != l_b.S_dyn:
        print('*** P!=S_dyn', dict(width=sample_d, S_dyn=dd(l_b.S_dyn), P=dd(l_b.P), S=dd(l_b.S), E=dd(l_b.S), para=list(enumerate(l_b.text_words,1))))
    expected_words = line_adjust.text_to_list_of_lines(sample_expected_text)
    assert all(' ' not in t for line in expected_words for t in line), expected_words
    assert all(' ' not in t for line in l_b_LINE_BREAKER_words for t in line), dict(l_b_LINE_BREAKER_words=l_b_LINE_BREAKER_words, P=l_b.P, W=l_b.W, text_words=l_b.text_words)
    if expected_words != l_b_LINE_BREAKER_words:
        print('>>>', dict(expected=expected_words, l_b=l_b_LINE_BREAKER_words))


# For debugging output of dicts:

def dd(d):
    return dict(sorted(d.items()))


# For outputting:


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


def main_test():
    assert list(line_adjust.split_paragraphs(PARAS)) == PARAS_SPLIT_EXPECTED

    with open('line-breaking-text-formatting.md') as paper_file:
        paper_paras = list(line_adjust.split_paragraphs(paper_file.read()))

    for para in paper_paras:
        para_words = para.split()
        one_line_words = ' '.join(para_words)
        print(one_line_words, flush=True)
        for format_width in range(1, len(one_line_words) + 1):
            print(' ', format_width, end='', flush=True)
            # print('---', 'width:', format_width, list(enumerate(para_words, 1))) # DO NOT SUBMIT
            para_b = line_break_from_paper.LineBreak(para_words, format_width)
            para_b.LINE_BY_LINE()
            para_b.LINE_BY_LINE_reversed()
            para_b.DYNAMIC()
            para_b.LINE_BREAKER()
            if para_b.S_dyn != para_b.P:
                print()
                print('***', dict(width=format_width, S_dyn=dd(para_b.S_dyn), P=dd(para_b.P), S=dd(para_b.S), E=dd(para_b.E), para=list(enumerate(para_words,1))))
        print()


if __name__ == "__main__":
    # print(line_adjust.pad_lines([['First', 'short', 'line'], ['second', 'and', 'longer', 'line'], ['last', 'line.']], 24))
    if True:
        import sys
        test_sample_text('''
                         a444 b444 c
                            d5555 e2
                         f33''',
                         '',
                         11)
        print()
        # sys.exit(1)
        test_sample_text(PAPER_TEXT, PAPER_EXPECTED_TEXT, PAPER_D)
        print()
        # sys.exit(1)
        # For figuring out how to read off the lines
        test_sample_text('The line-by-line method is the one that immediately comes to mind and has been used in many text formatting programs', '', 24)
        print()
        # sys.exit
        # This test broke some things while developing:
        test_sample_text('# On the Line Breaking Problem in Text Formatting', '# On the Line\nBreaking Problem\nin Text Formatting', 18)
        print()
        # sys.exit
        # This test happens to have to line breaks with exactly the same cost:
        test_sample_text('# On the Line Breaking Problem in Text Formatting', '# On the\nLine\nBreaking\nProblem\nin Text\nFormatting', 8)        # The sample from the paper.
        print()
        sys.exit(1)

    main_test()
