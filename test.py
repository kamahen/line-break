"""Test line_break_from_paper."""


import line_break_from_paper
import line_adjust


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

if __name__ == "__main__":
    assert list(line_adjust.split_paragraphs(PARAS)) == PARAS_EXPECTED


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
    print('words:', {i: (l_b.W[i], l_b.text_words[i-1]) for i in l_b.W.keys()})
    print('S:', dict(sorted(l_b.S.items())))
    print('E:', dict(sorted(l_b.E.items())))
    print('========== S')
    print(line_adjust.lines_of_words(l_b.S, l_b.W, text_words))
    print('========== E')
    print(line_adjust.lines_of_words(l_b.E, l_b.W, text_words))
    print('==========')

    l_b.DYNAMIC()
    print('DYNAMIC:', dict(sorted(l_b.S_dyn.items())))
    print('        ', dict(sorted(l_b.S_dyn2.items())))
    # print('C[(*,N]:', {i:(l_b.text_words[i-1], l_b.C[(i,l_b.N]) for i in from_to(1, l_b.N)})
    print('========== DYNAMIC')
    print(line_adjust.lines_of_words(l_b.S_dyn, l_b.W, text_words))
    print(line_adjust.lines_of_words(l_b.S_dyn2, l_b.W, text_words))
    print('==========')

    l_b.LINE_BREAKER()
    print('P:', dict(sorted(l_b.P.items())))
