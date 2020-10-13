# Implementation notes

## 1-origin indexing

The algorithms in the paper use 1-origin indexing and also a
2-dimensional array for the cost values. The easiest way of
representing this in Python is as a dict.

In some cases, the arrays are represented as sparse (e.g.,the `splits`
dict that I added to record optimal split points).

## Typos in the paper

None of the typos in the paper are serious, except for one in the
LINE-BREAKER algorithm. In computing `P`, there's clearly a bug with
`P[J] := K` because `P` is indexed by line number and `J` is a word
index.

## DYNAMIC and optimal splits

The paper doesn't describe how to extract the optimal split points,
but implies that it's easy.

The solution I came up with was to record whenever a new minimum value
of C[I,J] is computed for a potential line break. After all the cost
values are computed, a simple recurisve function collects these: if
words I-J were recorded as having a split (that is, a line break is
required and this is the optimal one), then collect the splits for
I-split and split+1-J.

In the LINE-BREAKER algorithm, only c[i,N] values are used (and
possibly, implicitly, c[1,i]). It appears from looking at the values,
that if we pick the minimum value for each "slack", this will also
produce optimal line-break positions. (I haven't proved this
rigorously, but it seems to apply for the test case.) This would be
equivalent to how LINE-BREAKER uses the cost matrix.

## c[i] and c[i,N]

c[i] is defined as c[i,N].

## P in LINE-BREAKER

The loop at the end confuses me ... it seems to do nothing more than
shift the values to the right (P[2:M-1] = P[1:M-2]) and throw away the
P[M-1] value. (P[1] and P[M] are, of course, special -- P[1] must
always be 1 and P[M] should always be S[M] (shortest possible last
line). But the question remains: why not just store the value in
P[I+1] instead of P[I] (and do a fix-up at the end for P[1], P[M])?

# Cost function

The cost function for formatting words _i_ to _j_ is defined as
follows (F<sub>i,j</sub> is the formatted length of words _i_ to
_j_):

* 2 if last line and words _i-j_ fit in 1 line
* 1 + 1/F<sub>i,j</sub> if not last line and words _i-j_ fit in 1 line
* 1 + min(C<sub>i,k</sub> * C<sub>k+1,j</sub>) otherwise

The computation for C<sub>i,N</sub> in LINE-BREAKER first sets
C<sub>N,N</sub> to 2.

There is a triple loop:
```
for i = m-1 .. 1:
  x = L[i] - 1 - W[S[i]]  # x: formatted length of line i without 1st word
  for j = S[i] .. E[i] by -1:  # i-th slack
    x = x + 1 + W[j]  # x: formatted length of line i add j-th word
    y = x + 1 + W[S[i+1]]  y: formatted length of line i add 1st word of line i+1
    C[j] = INFINITE
    for k = S[i+1] .. E[i+1] by -1:  i+1-th slack
      y = y - 1 - W[k]  # y: formatted length of line i without 1st word of line k
      # (1 + 1 / y) is C[W[S[i]],W[S[k]]-1]
      c[J] = min(c[J], (1 + 1 / y) * c[k])
      # set P[...] = J if new minimum ********* <= fix: P[...] => P[i]?
```
