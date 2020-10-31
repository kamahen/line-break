"""Test line_break_from_paper."""


import line_break_from_paper
import line_adjust
import sys
import textwrap


# The sample text from the paper:

SAMPLE_TEXT = """
  We  live in a print-oriented society. Every day
  we produce a huge volume of  printed  material,
  ranging   from  handbills  to  heavy  reference
  books.   Despite   the   mushroom   growth   of
  electronic   media,   print  remains  the  most
  versatile and most widely used medium for  mass
  communication.
"""

SAMPLE_EXPECTED_TEST = """
  We  live  in  a  print-oriented  society. Every
  day  we  produce  a  huge  volume  of   printed
  material,   ranging  from  handbills to   heavy
  reference books. Despite  the  mushroom  growth
  of  electronic  media,  print  remains the most
  versatile and most widely used medium for  mass
  communication.
"""

# D: maximum number of characters per line
SAMPLE_D = 47


PARAS = """
A line
Another line

Start new para

Another para
with a 2nd line
"""
PARAS_EXPECTED = ['A line\nAnother line', 'Start new para', 'Another para\nwith a 2nd line']


def test_sample_text():
    text_words = SAMPLE_TEXT.split()
    l_b = line_break_from_paper.LineBreak(text_words, SAMPLE_D)

    l_b.LINE_BY_LINE()
    l_b.LINE_BY_LINE_reversed()
    S_words = line_adjust.lines_of_words(l_b.S, l_b.W, text_words)
    print('==========')
    print('\n'.join(
        line_adjust.distribute_spaces(line, SAMPLE_D, i % 2 == 0)
        for i, line in enumerate(S_words)))
    # print('W:', l_b.W)
    print('words:', {i: (l_b.W[i], l_b.text_words[i-1]) for i in sorted(l_b.W.keys())})
    print('S:', dd(l_b.S))
    print('E:', dd(l_b.E))
    print('========== S')
    print(line_adjust.lines_of_words(l_b.S, l_b.W, l_b.text_words))
    print('========== E')
    print(line_adjust.lines_of_words(l_b.E, l_b.W, l_b.text_words))
    print('==========')

    l_b.DYNAMIC()
    print('DYNAMIC:', dd(l_b.S_dyn))
    # print('C[(*,N]:', {i:(l_b.text_words[i-1], l_b.C[(i,l_b.N]) for i in from_to(1, l_b.N)})
    print('========== DYNAMIC')
    l_b_words = line_adjust.lines_of_words(l_b.S_dyn, l_b.W, l_b.text_words)
    print(l_b_words)
    expected_words = line_adjust.text_to_list_of_lines(SAMPLE_EXPECTED_TEST)
    assert expected_words == l_b_words, dict(expected=expected_words, l_b=lb_words)
    print('==========')


# For debugging output of dicts:

def dd(d):
    return dict(sorted(d.items()))


def main_test():
    assert list(line_adjust.split_paragraphs(PARAS)) == PARAS_EXPECTED

    with open('line-breaking-text-formatting.md') as paper_file:
        paper_paras = list(line_adjust.split_paragraphs(paper_file.read()))

    for para in paper_paras:
        para_words = para.split()
        one_line_words = ' '.join(para_words)
        print(one_line_words, flush=True)
        for format_width in range(1, len(one_line_words) + 1):
            print(' ', format_width, end='', flush=True)
            # print('***', 'width:', format_width, list(enumerate(para_words, 1))) # DO NOT SUBMIT
            para_b = line_break_from_paper.LineBreak(para_words, format_width)
            para_b.LINE_BY_LINE()
            para_b.LINE_BY_LINE_reversed()
            para_b.DYNAMIC()
            # para_b.LINE_BREAKER()
        print()

    # The following is placed here because it crashes:
    l_b.LINE_BREAKER()
    print('P:', dd(l_b.P))


if __name__ == "__main__":
    if False: test_sample_text(); sys.exit(1)

    main_test()
