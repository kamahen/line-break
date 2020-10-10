"""Code in line-breaking-text-formatting.md, transcribed to Python

The original variable names have been retained, but using dicts rather
than arrays, to handle the 1-origin indexing of the algorithms.  The
code is not idiomatic Python, but has tried to stay as close as
possible to the original algorithm.

The algorithms have been packaged into a simple class, to allow the
"global" variables in table 1 (see the paper) to be shared. This is
not great programming style, but it's convenient.

The code requires Python 3.7 or later, to take advantage of the
ordering of a dict iterator being the same as collections.OrderedDict.
"""

import sys


assert sys.version_info >= (3, 7)


def from_to(from_i, to_i):
    return range(from_i, to_i + 1)


def from_downto(from_i, downto_i):
    return range(from_i, downto_i - 1, -1)


class LineBreak:
    """Global environment for the algorithms."""

    def __init__(self, text_words, D):

        self.text_words = text_words
        self.D = D

        # N: number of words in paragraph
        self.N = len(self.text_words)

        # W: number of characters in the I-th word (1-origin)
        self.W = {i: len(word) for i, word in enumerate(self.text_words, 1)}
        assert all(w > 0 for w in self.W.values())

        # self.M, self.S, self.L, self.E, self.P defined in
        # LINE_BY_LINE, LINE_BREAKER, LINE_BY_LINE_reversed


    def LINE_BY_LINE(self):
        """computes S[I]: index of first word in I-th line

        D,L,M,N,S,W are explained in table 1
        """

        # initialize
        self.M = 1               # number formated lines
        self.S = {1: 1}          # S[I] index of first word in I-th line
        self.L = {1: self.W[1]}  # L[I]: length of I-th formatted line

        for I in from_to(2, self.N):
            # add next word to current line
            self.L[self.M] = self.L[self.M] + 1 + self.W[I]

            if self.L[self.M] > self.D:
                self.L[self.M] = self.L[self.M] - 1 - self.W[I]

                # start new line
                self.M = self.M + 1
                self.S[self.M] = I
                self.L[self.M] = self.W[I]

        assert all(self.D >= len(' '.join(_line_words(self.S, self.W, self.text_words, i)))
                       for i in self.S.keys())


    def LINE_BY_LINE_reversed(self):
        """computes E[I]: index of first word in I-th line, earliest breaking.

        Assumes LINE_BY_LINE has been run
        """

        # This is essentially LINE_BY_LINE, done backwards, and not recording
        # things like M.

        self.E = {1: 1}
        curr_L = self.W[self.N]
        curr_M = self.M  # current line (counting down)

        for I in from_downto(self.N - 1, 1):
            curr_L = curr_L + 1 + self.W[I]
            if curr_L > self.D:
                self.E[curr_M] = I + 1
                curr_L = self.W[I]
                curr_M -= 1

        assert set(self.E.keys()) == set(self.S.keys())
        assert all(self.D >= len(' '.join(_line_words(self.E, self.W, self.text_words, i)))
                       for i in self.E.keys())
        assert all(self.E[i] <= self.S[i] for i in self.S.keys())


    def DYNAMIC(self):
        """computation of optimal cost C[1,N]
        C[I,J], F[I,J] explained in table 1.

        assumes LINE_BY_LINE has been called.
        """

        F = {}
        C = {}
        # initialize variables
        for I in from_to(1, self.N):
            for J in from_to(1, self.N):
                F[(I,J)] = 0
                C[(I,J)] = 0.0
            F[(I,J)] = self.W[I]
            C[(I,I)] = 1 + 1 / self.W[I]

        # compute upper diagonal of L and C
        # in reverse row order

        for I in from_downto(self.N - 1, 1):
            for J in from_to(I + 1, self.N):
                # calculate formatted length
                F[(I,J)] = F[(I,J-1)] + self.W[J] + 1
                if F[(I,J)] <= self.D:
                    # words I to J fit on line
                    if J == self.N:
                        C[(I,J)] = 2.0
                    else:
                        C[(I,J)] = 1 + 1 / F[(I,J)]
                else:
                    # words I to J have to be split
                    C[(I,J)] = C[(I,I)] * C[(I+1,J)]
                    for K in from_to(I + 1, J - 1):
                        T = C[(I,K)] * C[(K+1,J)]
                        if T < C[(I,J)]:
                            C[(I,J)] = T
        self.C = C


    def LINE_BREAKER(self):
        """computes: index of optimal first word in I-th line

        Assumes LINE_BY_LINE and LINE_BY_LINE_reversed have been called.

        Computation of optimal starting indices P[I]
        for M > 2.
        Assume S[I], E[I], L[I] (defined in table 1)
        have been computed. X,Y,Z are used to keep
        track of required lengths.
        INFINITE is any number larger than maximum
        possible cost c[I]
        """

        print('++', self.M, self.S)
        c = {self.S[self.M]: 2.0}
        self.P = {}
        INFINITE = sys.float_info.max

        # loop on lines backwards
        for I in from_downto(self.M - 1, 1):
            X = self.L[I] - 1 - self.W[self.S[I]]
            print({'I':I, 'X':X, 'L[I]':self.L[I], 'W[S[I]]':self.W[self.S[I]]})

            # loop over I-th slack
            assert self.S[I] >= self.E[I]
            for J in from_downto(self.S[I], self.E[I]):
                X = X + 1 + self.W[J]
                Y = X + 1 + self.W[self.S[I+1]]
                c[J] = INFINITE

                # loop over (I+1)-th slack
                assert self.S[I+1] >= self.E[I+1]
                print({'J':J, 'X':X, 'Y':Y, 'c':c})
                for K in from_downto(self.S[I+1], self.E[I+1]):
                    Y = Y - 1 - self.W[K]
                    print({'K':K, 'Y': Y, '<=':Y <= self.D, 'c':c, 'P':self.P})
                    if Y <= self.D:
                        # update c[J]
                        Z = (1.0 + 1.0 / Y) * c[K]
                        if Z < c[J]:
                            c[J] = Z
                            self.P[J] = K

        # retrieve optimal starting indices
        self.P[self.M] = self.S[self.M]
        J = self.P[1]
        self.P[1] = 1
        for I in from_to(2, self.M - 1):
            K = self.P[I]
            self.P[I] = J
            J = K


def lines_of_words(S, W, text_words):
    """Convert index of first words to list of lines

    This function is not in the original paper; it has been added here
    to handle the output nicely. It takes the "S" that's computed by a
    line breaking algorithm and converts it to a list of lines, where
    each line is a list of words.
    """

    assert sorted(S.keys()) == list(range(1, 1+max(S.keys()))), [sorted(S.keys()), list(range(1, 1+max(S.keys())))]
    return [_line_words(S, W, text_words, i) for i in sorted(S.keys())]


def _line_words(S, W, text_words, i):
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

# D: maximum number of characters per line
SAMPLE_D = 47


if __name__ == "__main__":
    text_words = SAMPLE_TEXT.split()

    l_b = LineBreak(text_words, SAMPLE_D)

    l_b.LINE_BY_LINE()
    l_b.LINE_BY_LINE_reversed()
    S_words = lines_of_words(l_b.S, l_b.W, text_words)
    print('==========')
    print('\n'.join(distribute_spaces(line, SAMPLE_D, i % 2 == 0)
                    for i, line in enumerate(S_words)))
    print('W:', l_b.W)
    print('words:', {i: (l_b.W[i], l_b.text_words[i-1]) for i in l_b.W.keys()})
    print('S:', l_b.S)
    print('E:', l_b.E)
    print('========== S')
    print(lines_of_words(l_b.S, l_b.W, text_words))
    print('========== E')
    print(lines_of_words(l_b.E, l_b.W, text_words))
    print('==========')

    if False:
        l_b.DYNAMIC()
        print('========== C')
        C_i_max = max(i for i,_ in l_b.C.keys())
        C_j_max = max(j for _,j in l_b.C.keys())
        for i in from_to(1, C_i_max):
            print([l_b.C[(i,j)] for j in from_to(1, C_j_max)])
        print('==========')

    l_b.LINE_BREAKER()
    print('P:', l_b.P)
