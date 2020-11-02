"""Test line_break_from_paper."""


import sys
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
    text_words = sample_text.split()
    l_b = line_break_from_paper.LineBreak(text_words, sample_d)

    l_b.LINE_BY_LINE()
    l_b.LINE_BY_LINE_reversed()
    S_words = line_adjust.lines_of_words(l_b.S, l_b.W, text_words)
    print('==========')
    print('\n'.join(
        line_adjust.distribute_spaces(line, sample_d, i % 2 == 0)
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
    print('DYNAMIC:', len(l_b.S_dyn), dd(l_b.S_dyn))
    # print('C[(*,N]:', {i:(l_b.text_words[i-1], l_b.C[(i,l_b.N]) for i in from_to(1, l_b.N)})
    print('========== DYNAMIC')
    l_b_words = line_adjust.lines_of_words(l_b.S_dyn, l_b.W, l_b.text_words)
    print(l_b_words)
    expected_words = line_adjust.text_to_list_of_lines(sample_expected_text)
    assert expected_words == l_b_words, dict(expected=expected_words, l_b=l_b_words)
    print('==========')

    l_b.LINE_BREAKER()
    print('P:', len(l_b.P), dd(l_b.P))


# For debugging output of dicts:

def dd(d):
    return dict(sorted(d.items()))


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
            # print('***', 'width:', format_width, list(enumerate(para_words, 1))) # DO NOT SUBMIT
            para_b = line_break_from_paper.LineBreak(para_words, format_width)
            para_b.LINE_BY_LINE()
            para_b.LINE_BY_LINE_reversed()
            para_b.DYNAMIC()
            para_b.LINE_BREAKER()
            if para_b.S_dyn != para_b.P:
                print()
                assert para_b.S_dyn == para_b.P, dict(width=format_width, S_dyn=dd(para_b.S_dyn), P=dd(para_b.P), para=[(i,w) for i,w in enumerate(para_words,1)])
        print()


if __name__ == "__main__":
    if True:
        test_sample_text(PAPER_TEXT, PAPER_EXPECTED_TEXT, PAPER_D)
        # sys.exit(1)

    main_test()
