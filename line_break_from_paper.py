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

# pylint: disable=invalid-name,fixme,line-too-long,bad-whitespace,too-many-instance-attributes,missing-function-docstring

import sys
from typing import Dict, List, Tuple

# INFINITE is any number larger than maximum
INFINITE = sys.float_info.max

assert sys.version_info >= (3, 7)


def from_to(from_i, to_i):
    return range(from_i, to_i + 1)


def from_downto(from_i, downto_i):
    return range(from_i, downto_i - 1, -1)


class LineBreak:
    """Global environment for the algorithms."""

    # Dict's simulate 1-origin arrays

    text_words: List[str]           # list of words in paragraph (0-index) - not in paper - see also self.text_word()
    D: int                          # max number of chars per line
    N: int                          # number of words in paragraph
    W: Dict[int,int]                # number of chars in I-th word

    # Other attributes (not defined in __init__ but crated by
    # LINE_BY_LINE, LINE_BY_LINE_reversed, LINE_BREAKER), to make
    # pylint be quiet:
    M: int                          # number of formatted lines
    L: Dict[int,int]                # length of I-th formatted line
    E: Dict[int,int]                # index of first word, line I, earliest breaking
    C: Dict[Tuple[int,int], float]  # cost function (from I-th to J-th word)
    F: Dict[Tuple[int,int], int]    # formatted length from I-th to -J-th word
    S: Dict[int,int]                # index of first word in I-th line from LINE_BY_LINE

    # Not in the paper:
    S_dyn: Dict[int,int]            # S from DYNAMIC
    P: Dict[int,int]                # S from LINE_BREAKER


    def __init__(self, text_words, D):

        assert all(' ' not in t for t in text_words), text_words
        self.text_words = text_words
        self.D = D
        self.N = len(self.text_words)

        self.W = {i: min(len(word), D) for i, word in enumerate(self.text_words, 1)}
        assert all(w > 0 for w in self.W.values())


    def text_word(self, i):
        """1-index into self.text_words."""
        return self.text_words[i - 1]


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


    def LINE_BY_LINE_reversed(self):
        """computes E[I]: index of first word in I-th line, earliest breaking.

        Assumes LINE_BY_LINE has been run.
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

        assert set(self.E) == set(self.S)
        assert all(self.E[i] <= self.S[i] for i in self.S)


    def DYNAMIC(self):
        """computation of optimal cost C[(1,N)]
        C[(I,J)], F[(I,J)] explained in table 1.

        Assumes LINE_BY_LINE has been called.

        The computation of S_dyn is in addition to the paper's code.
        """

        if len(' '.join(self.text_words)) <= self.D or len(self.text_words) <= 1:
            # TODO: do we need this short-circuit? There are 2 cases:
            # a piece of text that's only a single line or that consists
            # of a single long word.
            self.C = {}  # This is incorrect but doesn't matter
            self.S_dyn = {1:1}
            return

        F = {}
        C = {}
        # initialize variables
        for I in from_to(1, self.N):
            for J in from_to(1, self.N):
                F[(I,J)] = 0
                C[(I,J)] = 0.0
            F[(I,I)] = self.W[I]
            C[(I,I)] = 1.0 + 1.0 / self.W[I]  # TODO: see Notes.md#Cost_function

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
                        C[(I,J)] = 1.0 + 1.0 / F[(I,J)]  # TODO: see Notes.md#Cost_function
                else:
                    # words I to J have to be split
                    C[(I,J)] = C[(I,I)] * C[(I+1,J)] # TODO: see Notes.md#Cost_function_for_line_breaks
                    for K in from_to(I + 1, J - 1):
                        T = C[(I,K)] * C[(K+1,J)]  # TODO: see Notes.md#Cost_function_for_line_breaks
                        if T < C[(I,J)]:
                            C[(I,J)] = T
        self.C = C
        self.F = F
        # self.print_C()  # DO NOT SUBMIT

        # retrieve optimal starting indices (this is not in the published code)
        # into self.S_dyn.

        starts = [self.S[self.M]]
        while True:
            K = starts[0] - 1
            if self.F[(1,K)] <= self.D:
                starts.insert(0, 1)
                break
            starts.insert(0, self.split_point(K))
        self.S_dyn = dict(enumerate(starts, 1))


    def split_point(self, end_K):
        assert self.F[(1,end_K)] > self.D
        line_words = [K for K in from_to(1,end_K) if self.F[(K,end_K)] <= self.D]
        # The reversed(...) in the following is for tie-breaks that
        # match what LINE_BREAKER does.
        Cs = [(self.C[(1,K-1)]*self.C[(K,end_K)], K) for K in reversed(line_words)]  # TODO: generator
        _, point = min(Cs, key=lambda c_k: c_k[0])
        # print('***split', (point, self.text_word(point)), 'end_K:', end_K, line_words, 'Cs:', [(c,n,self.text_word(n)) for c,n in Cs], 'F:', {K:self.F[(K,end_K)] for K in from_to(1,end_K)}, 'D:', self.D)  # DO NOT SUBMIT
        return point


    def print_C(self): # for debugging
        print('~~~~~')
        print('{:>3s}'.format(' '), end='')
        for j in from_to(1,self.N):
            print(' {:>8d}'.format(j), end='')
        print()
        for i in from_to(1,self.N):
            print('{:>3d}'.format(i), end='')
            for j in from_to(1,self.N):
                if self.C[(i,j)] == 0.0:
                    print(' {:>8s}'.format('0'), end='')
                else:
                    print(' {:>8.5f}'.format(self.C[(i,j)]), end='')
            print()
        print('~~~~~')


    def LINE_BREAKER(self):
        """computes: index of optimal first word in I-th line

        Assumes LINE_BY_LINE and LINE_BY_LINE_reversed have been called.

        Computation of optimal starting indices P[I]
        for M > 2.
        Assume S[I], E[I], L[I] (defined in table 1)
        have been computed. X,Y,Z are used to keep
        track of required lengths.
        (c[I] is cost function = C[(I,N] (N = # words in paragraph)
        possible cost c[I]
        """

        c = {self.S[self.M]: 2.0}
        # c = {J: 2.0 for J in from_to(1, self.N)}  # <==== TODO: is this correct, to avoid "K in c" test below?
        self.P = {}
        P2 = {1:1, self.M:self.S[self.M]}  # Not in paper - an alternative way of computing P
        assert len(self.S) == len(self.E)  # TODO: added
        assert all(self.S[i] >= self.E[i] for i in from_to(1, len(self.S)))  # TODO: added

        # loop on lines backwards
        for I in from_downto(self.M - 1, 1):
            X = self.L[I] - 1 - self.W[self.S[I]]

            # loop over I-th slack
            for J in from_downto(self.S[I], self.E[I]):
                X = X + 1 + self.W[J]
                Y = X + 1 + self.W[self.S[I+1]]
                c[J] = INFINITE

                # loop over (I+1)-th slack
                assert self.S[I+1] >= self.E[I+1]
                for K in from_downto(self.S[I+1], self.E[I+1]):
                    Y = Y - 1 - self.W[K]
                    if Y <= self.D and K in c:  # TODO: added "if K in c"
                        # update c[J]
                        Z = (1.0 + 1.0 / Y) * c[K]  # TODO: see Notes.md#Cost_function
                        if Z < c[J]:
                            c[J] = Z
                            self.P[I] = K  # <=== TODO: "P[J]" in the original is clearly wrong.
                            P2[I+1] = K  # TODO: not in paper

        # retrieve optimal starting indices
        # print('P(1):', dd(self.P))  # DO NOT SUBMIT
        self.P[self.M] = self.S[self.M]
        J = self.P[1]
        self.P[1] = 1
        for I in from_to(2, self.M - 1):
            K = self.P[I]
            self.P[I] = J
            J = K
        # print('P(2):', dd(self.P))  # DO NOT SUBMIT
        assert P2 == self.P
        # print('S_dyn:', dd(self.S_dyn))  # DO NOT SUBMIT


# For debugging output of dicts:

def dd(d):
    return dict(sorted(d.items()))
