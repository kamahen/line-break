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
import line_adjust

# INFINITE is any number larger than maximum
INFINITE = sys.float_info.max

assert sys.version_info >= (3, 7)


def from_to(from_i, to_i):
    assert from_i <= to_i, ['from_to', from_i, to_i]
    return range(from_i, to_i + 1)


def from_downto(from_i, downto_i):
    assert from_i >= downto_i, ['from_downto', from_i, downto_i]
    return range(from_i, downto_i - 1, -1)


class LineBreak:
    """Global environment for the algorithms."""

    def __init__(self, text_words, D):

        self.text_words = text_words
        self.D = D

        # N: number of words in paragraph
        self.N = len(self.text_words)

        # W: number of characters in the I-th word (1-origin)
        self.W = {i: min(len(word), D) for i, word in enumerate(self.text_words, 1)}
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

        assert all(self.D >= len(' '.join(
            line_adjust.line_words(self.S, self.W, self.text_words, i)))
                   for i in self.S.keys())

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

        assert set(self.E.keys()) == set(self.S.keys())
        assert all(self.D >= len(' '.join(line_adjust.line_words(self.E, self.W, self.text_words, i)))
                       for i in self.E.keys())
        assert all(self.E[i] <= self.S[i] for i in self.S.keys())

    def DYNAMIC(self):
        """computation of optimal cost C[(1,N)]
        C[(I,J)], F[(I,J)] explained in table 1.

        Assumes LINE_BY_LINE has been called.

        The splits dict and computation of S_dyn are in addition to
        the paper's code.
        """

        F = {}
        C = {}
        splits = {}
        # initialize variables
        for I in from_to(1, self.N):
            for J in from_to(1, self.N):
                F[(I,J)] = 0
                C[(I,J)] = 0.0
            F[(I,I)] = self.W[I]
            C[(I,I)] = 1.0 + 1.0 / self.W[I]

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
                        # splits[(I,J)] = None
                    else:
                        C[(I,J)] = 1.0 + 1.0 / F[(I,J)]
                        # splits[(I,J)] = None
                else:
                    # words I to J have to be split
                    C[(I,J)] = C[(I,I)] * C[(I+1,J)]
                    splits[(I,J)] = I + 1
                    for K in from_to(I + 1, J - 1):
                        #  c[(I,J)] = min(C[(I,J)], C[(I,K)] * C[(K+1,J)])
                        T = C[(I,K)] * C[(K+1,J)]
                        if T < C[(I,J)]:
                            C[(I,J)] = T
                            splits[(I,J)] = K
        self.C = C

        # retrieve optimal starting indices
        # (this is not in the published code)

        def optimal_splits(I, J):
            assert I <= J and I >= 1 and J <= self.N
            split = splits[(I,J)] if (I,J) in splits else None
            if split:
                yield from optimal_splits(I, split)
                yield from optimal_splits(split + 1, J)
            else:
                yield I

        self.S_dyn = dict(enumerate(optimal_splits(1, self.N), 1))

        # A different way of extracting the split points.
        # Assumes that E has been computed
        self.S_dyn2 = {1: 1, self.M: self.S[self.M]}
        for I in from_downto(self.M-1, 2):
            min_C = INFINITE
            # print('dyn2:', I, {i: (self.text_words[i-1], C[(i,self.N)]) for i in from_to(self.E[I], self.S[I])})
            for J in from_to(self.E[I], self.S[I]):
                # Only the "otherwise" case of C[(I,J)] calculation applies
                new_C = 1.0 + C[(1,J)] * C[(J+1,self.N)]
                if new_C < min_C:  # and F[(J,self.S_dyn2[I+1]-1)] <= self.D:
                    min_C = new_C
                    self.S_dyn2[I] = J + 1

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
        # c = {J: 2.0 for J in from_to(1, self.N)}  # <==== TODO: is this correct?
        # print('++', {'M':self.M, 'S':self.S, 'c':c})
        self.P = {}

        # loop on lines backwards
        for I in from_downto(self.M - 1, 1):
            X = self.L[I] - 1 - self.W[self.S[I]]
            # print({'I':I, 'X':X, 'L[I]':self.L[I], 'W[S[I]]':self.W[self.S[I]], 'S[I]':self.S[I], 'E[I]':self.E[I]})

            # loop over I-th slack
            assert self.S[I] >= self.E[I]
            for J in from_downto(self.S[I], self.E[I]):
                X = X + 1 + self.W[J]
                Y = X + 1 + self.W[self.S[I+1]]
                c[J] = INFINITE

                # loop over (I+1)-th slack
                assert self.S[I+1] >= self.E[I+1]
                # print(' ', {'J':J, 'X':X, 'Y':Y, 'c':c, 'S[I+1]':self.S[I+1], 'E[I+1]':self.E[I+1]})
                for K in from_downto(self.S[I+1], self.E[I+1]):
                    Y = Y - 1 - self.W[K]
                    # print('   ', {'K':K, 'Y':Y, 'Y<=D':Y <= self.D, 'c':c, 'P':self.P})
                    if Y <= self.D:
                        # update c[J]
                        Z = (1.0 + 1.0 / Y) * c[K]
                        if Z < c[J]:
                            c[J] = Z
                            self.P[I] = K  # <=== TODO: "J" is clearly wrong. Should it be I?

        # retrieve optimal starting indices
        print('P(1):', dict(sorted(self.P.items())))
        self.P[self.M] = self.S[self.M]
        J = self.P[1]
        self.P[1] = 1
        for I in from_to(2, self.M - 1):
            K = self.P[I]
            self.P[I] = J
            J = K
        print('P(2):', dict(sorted(self.P.items())))


